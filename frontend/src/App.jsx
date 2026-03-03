import { useState, useCallback } from "react";
import IncidentDashboard from "./components/IncidentDashboard";
import { streamFetch } from "./lib/streamFetch";

/**
 * Phase lifecycle:
 *   idle → analyzing → awaiting_approval → remediating → complete | error
 *
 * tokens accumulates input/output counts from both agent calls and is shown
 * in the completion summary. It resets with the rest of the workflow state.
 */

const INITIAL_STEPS = [
  {
    id: "analyze",
    index: 0,
    label: "Analyze Logs",
    tool: "analyze_logs",
    description: "Read CloudWatch logs and generate root cause hypotheses",
    status: "pending", // pending | running | complete | error
    toolEvents: [],    // { kind: "executing"|"result", message, summary, detail }
    text: "",          // streaming model output
    hypotheses: null,  // structured output: { hypotheses: [...], recommended_action }
  },
  {
    id: "remediate",
    index: 1,
    label: "Increase Lambda Concurrency",
    tool: "increase_lambda_concurrency",
    description: "Raise reserved concurrency from 10 → 20 via AWS API",
    status: "pending",
    toolEvents: [],
    text: "",
  },
];

export default function App() {
  const [phase, setPhase] = useState("idle");
  const [steps, setSteps] = useState(INITIAL_STEPS);
  const [error, setError] = useState(null);
  const [tokens, setTokens] = useState({ input: 0, output: 0 });

  const patchStep = useCallback((id, patch) => {
    setSteps((prev) =>
      prev.map((s) => (s.id === id ? { ...s, ...patch } : s))
    );
  }, []);

  const appendStepText = useCallback((id, chunk) => {
    setSteps((prev) =>
      prev.map((s) => (s.id === id ? { ...s, text: s.text + chunk } : s))
    );
  }, []);

  const pushToolEvent = useCallback((id, evt) => {
    setSteps((prev) =>
      prev.map((s) =>
        s.id === id ? { ...s, toolEvents: [...s.toolEvents, evt] } : s
      )
    );
  }, []);

  // -------------------------------------------------------------------------
  // Start incident — runs the analysis agent
  // -------------------------------------------------------------------------
  const startIncident = useCallback(async () => {
    setPhase("analyzing");
    setError(null);
    setSteps(INITIAL_STEPS);
    patchStep("analyze", { status: "running" });

    await streamFetch(
      "/api/start-incident",
      (event) => {
        switch (event.type) {
          case "tool_start":
            pushToolEvent("analyze", { kind: "start", message: event.message, tool: event.tool });
            break;
          case "tool_executing":
            pushToolEvent("analyze", { kind: "executing", message: event.message });
            break;
          case "tool_result":
            pushToolEvent("analyze", { kind: "result", summary: event.summary, detail: event.detail });
            break;
          case "text_chunk":
            // Model streams raw JSON during analysis — suppress it; structured
            // result arrives via analysis_complete.hypotheses instead.
            break;
          case "analysis_complete":
            setSteps((prev) =>
              prev.map((s) =>
                s.id === "analyze"
                  ? { ...s, status: "complete", text: s.text || event.text, hypotheses: event.hypotheses ?? null }
                  : s
              )
            );
            // Step 1 of 2 token accumulation — remediation_complete adds step 2.
            if (event.usage) {
              setTokens((prev) => ({
                input: prev.input + (event.usage.inputTokens || 0),
                output: prev.output + (event.usage.outputTokens || 0),
              }));
            }
            setPhase("awaiting_approval");
            break;
          case "error":
            patchStep("analyze", { status: "error", text: event.message });
            setPhase("error");
            setError(event.message);
            break;
          default:
            break;
        }
      },
      (err) => {
        patchStep("analyze", { status: "error" });
        setPhase("error");
        setError(err);
      }
    );
  }, [patchStep, appendStepText, pushToolEvent]);

  // -------------------------------------------------------------------------
  // Approve remediation — runs the remediation agent
  // -------------------------------------------------------------------------
  const approveRemediation = useCallback(async () => {
    setPhase("remediating");
    patchStep("remediate", { status: "running" });

    await streamFetch(
      "/api/approve-remediation",
      (event) => {
        switch (event.type) {
          case "tool_start":
            pushToolEvent("remediate", { kind: "start", message: event.message, tool: event.tool });
            break;
          case "tool_executing":
            pushToolEvent("remediate", { kind: "executing", message: event.message });
            break;
          case "tool_result":
            pushToolEvent("remediate", { kind: "result", summary: event.summary, detail: event.detail });
            break;
          case "text_chunk":
            appendStepText("remediate", event.content);
            break;
          case "remediation_complete":
            setSteps((prev) =>
              prev.map((s) =>
                s.id === "remediate"
                  ? { ...s, status: "complete", text: s.text || event.text }
                  : s
              )
            );
            // Step 2 of 2 — combined total now reflects the full end-to-end cost.
            if (event.usage) {
              setTokens((prev) => ({
                input: prev.input + (event.usage.inputTokens || 0),
                output: prev.output + (event.usage.outputTokens || 0),
              }));
            }
            setPhase("complete");
            break;
          case "error":
            patchStep("remediate", { status: "error", text: event.message });
            setPhase("error");
            setError(event.message);
            break;
          default:
            break;
        }
      },
      (err) => {
        patchStep("remediate", { status: "error" });
        setPhase("error");
        setError(err);
      }
    );
  }, [patchStep, appendStepText, pushToolEvent]);

  // Rejection is client-side only — no backend call is made. Phase is set to
  // "error" so the UI shows a consistent rejected/error state.
  const rejectRemediation = useCallback(() => {
    patchStep("remediate", { status: "error", text: "Remediation rejected by operator." });
    setPhase("error");
    setError("Remediation rejected by operator.");
  }, [patchStep]);

  const reset = useCallback(() => {
    setPhase("idle");
    setSteps(INITIAL_STEPS);
    setError(null);
    setTokens({ input: 0, output: 0 });
  }, []);

  return (
    <IncidentDashboard
      phase={phase}
      steps={steps}
      error={error}
      tokens={tokens}
      onStartIncident={startIncident}
      onApprove={approveRemediation}
      onReject={rejectRemediation}
      onReset={reset}
    />
  );
}
