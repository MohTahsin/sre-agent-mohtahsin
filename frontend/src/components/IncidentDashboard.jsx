import AgentStep from "./AgentStep";
import ApprovalGate from "./ApprovalGate";

const SEVERITY_BADGE = "bg-red-900/60 text-brand-red border border-brand-red/40";
const P1_DOT = "inline-block w-2 h-2 rounded-full bg-brand-red animate-ping mr-1.5";

export default function IncidentDashboard({
  phase,
  steps,
  error,
  tokens,
  onStartIncident,
  onApprove,
  onReject,
  onReset,
}) {
  // Derived booleans to avoid repeating phase string comparisons throughout the JSX.
  const isIdle = phase === "idle";
  const isComplete = phase === "complete";
  const isError = phase === "error";
  const isActive = !isIdle && !isComplete && !isError;

  return (
    <div className="min-h-screen flex flex-col bg-surface-0 text-gray-200 font-mono">
      {/* ------------------------------------------------------------------ */}
      {/* Top bar                                                              */}
      {/* ------------------------------------------------------------------ */}
      <header className="border-b border-surface-3 bg-surface-1 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-brand-blue font-semibold text-sm tracking-wide">
            ⚡ SRE Agent
          </span>
          <span className="text-surface-3">|</span>
          <span className="text-xs text-gray-500">Powered by Grok · Strands Agents</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-brand-green inline-block" />
          grok-4-1-fast-reasoning
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* Incident banner                                                      */}
      {/* ------------------------------------------------------------------ */}
      <div className="border-b border-surface-3 bg-surface-1/50 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-1">
              {isActive && <span className={P1_DOT} />}
              {!isActive && isComplete && (
                <span className="inline-block w-2 h-2 rounded-full bg-brand-green mr-1.5" />
              )}
              {!isActive && !isComplete && (
                <span className="inline-block w-2 h-2 rounded-full bg-gray-600 mr-1.5" />
              )}
              <span className={`text-xs px-2 py-0.5 rounded font-semibold ${SEVERITY_BADGE}`}>
                P1 INCIDENT
              </span>
              <span className="text-xs text-gray-500">INC-20240303-001</span>
            </div>
            <h1 className="text-base font-semibold text-gray-100">
              payments-processor-prod — Lambda Throttling
            </h1>
            <p className="text-xs text-gray-500 mt-0.5">
              Error rate: ~45% · Reserved concurrency: 10/10 ·{" "}
              <span className="text-brand-orange">TooManyRequestsException</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            {isIdle && (
              <button
                onClick={onStartIncident}
                className="px-5 py-2 rounded bg-brand-red hover:bg-red-500 text-white text-sm font-semibold transition-colors shadow"
              >
                🚨 Start Incident
              </button>
            )}
            {(isComplete || isError) && (
              <button
                onClick={onReset}
                className="px-4 py-2 rounded bg-surface-2 hover:bg-surface-3 text-gray-300 text-sm transition-colors border border-surface-3"
              >
                ↺ Reset
              </button>
            )}
            {isComplete && (
              <span className="px-3 py-1.5 rounded bg-green-900/50 border border-brand-green/40 text-brand-green text-xs font-semibold">
                ✓ Incident Resolved
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Main content                                                         */}
      {/* ------------------------------------------------------------------ */}
      <main className="flex-1 px-6 py-6">
        <div className="max-w-5xl mx-auto space-y-4">

          {/* Idle splash */}
          {isIdle && (
            <div className="text-center py-20 animate-fade-in">
              <p className="text-4xl mb-4">🤖</p>
              <p className="text-gray-400 text-sm mb-1">
                Grok SRE Agent is standing by.
              </p>
              <p className="text-gray-600 text-xs">
                Click <span className="text-brand-red font-semibold">Start Incident</span> to begin automated investigation.
              </p>
            </div>
          )}

          {/* Step 1 — Analysis */}
          {!isIdle && (
            <AgentStep step={steps[0]} stepNumber={1} />
          )}

          {/* Human approval gate — shown after analysis completes */}
          {(phase === "awaiting_approval") && (
            <ApprovalGate
              step={steps[1]}
              onApprove={onApprove}
              onReject={onReject}
            />
          )}

          {/* Step 2 — Remediation (shown once approved) */}
          {(phase === "remediating" || phase === "complete") && (
            <AgentStep step={steps[1]} stepNumber={2} />
          )}

          {/* Error step 2 after reject */}
          {phase === "error" && steps[1].status === "error" && steps[0].status === "complete" && (
            <AgentStep step={steps[1]} stepNumber={2} />
          )}

          {/* Global error banner */}
          {isError && error && steps[0].status !== "complete" && (
            <div className="rounded-lg border border-brand-red/40 bg-red-950/30 p-4 text-sm text-brand-red animate-fade-in">
              <span className="font-semibold">Agent error: </span>{error}
            </div>
          )}

          {/* Complete summary */}
          {isComplete && (
            <div className="rounded-lg border border-brand-green/30 bg-green-950/20 p-4 text-sm animate-fade-in">
              <p className="text-brand-green font-semibold mb-1">✓ Remediation complete</p>
              <p className="text-gray-400 text-xs">
                <code className="text-brand-blue">payments-processor-prod</code> reserved concurrency
                has been raised from <span className="text-brand-red">10</span> to{" "}
                <span className="text-brand-green">20</span>. Monitor error rate over the next 2–3
                minutes to confirm recovery.
              </p>
              {/* Only shown when at least one agent returned usage data; guards against an empty {} fallback. */}
              {tokens && (tokens.input > 0 || tokens.output > 0) && (
                <div className="mt-3 pt-3 border-t border-brand-green/20 flex items-center gap-4 text-xs text-gray-500">
                  <span className="text-gray-600 uppercase tracking-wider">Tokens used</span>
                  <span>
                    <span className="text-gray-400">in</span>{" "}
                    <span className="text-brand-blue font-semibold">{tokens.input.toLocaleString()}</span>
                  </span>
                  <span>
                    <span className="text-gray-400">out</span>{" "}
                    <span className="text-brand-blue font-semibold">{tokens.output.toLocaleString()}</span>
                  </span>
                  <span>
                    <span className="text-gray-400">total</span>{" "}
                    <span className="text-brand-blue font-semibold">{(tokens.input + tokens.output).toLocaleString()}</span>
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
