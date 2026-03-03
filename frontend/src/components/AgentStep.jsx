import StreamingText from "./StreamingText";

// Maps Grok's categorical confidence label to Tailwind colour tokens.
// The ?? fallback in the badge handles any unexpected values gracefully.
const CONFIDENCE_STYLES = {
  High:   "text-brand-green  border-brand-green/40  bg-green-950/30",
  Medium: "text-brand-yellow border-brand-yellow/40 bg-yellow-950/20",
  Low:    "text-gray-400     border-gray-600/40     bg-surface-2",
};

// Renders structured output from Grok's response_format schema.
// Each card corresponds to one Hypothesis object in HypothesisReport.
function HypothesisCards({ report }) {
  return (
    <div className="space-y-2">
      {report.hypotheses.map((h) => (
        <div key={h.rank} className="rounded border border-surface-3 bg-surface-0/60 p-3">
          <div className="flex items-start justify-between gap-3 mb-1.5">
            <span className="text-xs font-semibold text-brand-blue leading-snug">
              #{h.rank} — {h.title}
            </span>
            <span className={`text-xs px-1.5 py-0.5 rounded border font-semibold shrink-0 ${CONFIDENCE_STYLES[h.confidence] ?? CONFIDENCE_STYLES.Low}`}>
              {h.confidence}{h.confidence_pct != null ? ` (${h.confidence_pct}%)` : ""}
            </span>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">{h.evidence}</p>
        </div>
      ))}
      {report.recommended_action && (
        <div className="rounded border border-brand-orange/30 bg-orange-950/20 p-3">
          <span className="text-xs font-semibold text-brand-orange">Recommended Action: </span>
          <span className="text-xs text-gray-300">{report.recommended_action}</span>
        </div>
      )}
    </div>
  );
}

const STATUS_CONFIG = {
  pending: {
    dot: "bg-gray-600",
    label: "Pending",
    labelColor: "text-gray-500",
    border: "border-surface-3",
    bg: "bg-surface-1/30",
  },
  running: {
    dot: "bg-brand-blue animate-ping",
    label: "Running",
    labelColor: "text-brand-blue",
    border: "border-brand-blue/40",
    bg: "bg-surface-1",
  },
  complete: {
    dot: "bg-brand-green",
    label: "Complete",
    labelColor: "text-brand-green",
    border: "border-brand-green/30",
    bg: "bg-surface-1",
  },
  error: {
    dot: "bg-brand-red",
    label: "Error",
    labelColor: "text-brand-red",
    border: "border-brand-red/30",
    bg: "bg-surface-1",
  },
};

function ToolEventRow({ evt }) {
  if (evt.kind === "start") {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-500 py-0.5">
        <span className="text-brand-purple">›</span>
        <span>Tool invoked:</span>
        <code className="text-brand-purple">{evt.tool}</code>
      </div>
    );
  }
  if (evt.kind === "executing") {
    return (
      <div className="flex items-center gap-2 text-xs text-brand-yellow py-0.5 animate-fade-in">
        <span>⚙</span>
        <span>{evt.message}</span>
      </div>
    );
  }
  if (evt.kind === "result") {
    return (
      <div className="animate-fade-in">
        <div className="flex items-center gap-2 text-xs text-brand-green py-0.5">
          <span>✓</span>
          <span>{evt.summary}</span>
        </div>
        {evt.detail && (
          <pre className="mt-1 ml-4 text-xs text-gray-500 bg-surface-0 rounded p-2 overflow-x-auto">
            {JSON.stringify(evt.detail, null, 2)}
          </pre>
        )}
      </div>
    );
  }
  return null;
}

export default function AgentStep({ step, stepNumber }) {
  const cfg = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending;
  // isStreaming: true only while text is actively arriving; drives the blinking cursor in StreamingText.
  const isStreaming = step.status === "running" && step.text.length > 0;

  return (
    <div
      className={`rounded-lg border ${cfg.border} ${cfg.bg} overflow-hidden animate-slide-in transition-colors duration-300`}
    >
      {/* Step header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-surface-3/60">
        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-surface-2 text-xs font-semibold text-gray-400 shrink-0">
          {stepNumber}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-gray-100">{step.label}</span>
            <code className="text-xs text-gray-500 bg-surface-2 px-1.5 py-0.5 rounded">
              {step.tool}()
            </code>
          </div>
          <p className="text-xs text-gray-500 mt-0.5 truncate">{step.description}</p>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
          <span className={`text-xs font-medium ${cfg.labelColor}`}>{cfg.label}</span>
        </div>
      </div>

      {/* Tool events */}
      {step.toolEvents.length > 0 && (
        <div className="px-4 py-2 border-b border-surface-3/40 space-y-0.5 bg-surface-0/40">
          {step.toolEvents.map((evt, i) => (
            <ToolEventRow key={i} evt={evt} />
          ))}
        </div>
      )}

      {/* Structured output — analysis step only (hypotheses from Grok's response_format) */}
      {step.hypotheses && (
        <div className="px-4 py-3">
          <div className="text-xs text-gray-600 mb-2 uppercase tracking-wider">Hypotheses</div>
          <HypothesisCards report={step.hypotheses} />
        </div>
      )}

      {/* Free-text output — remediation step (agent explains what was done and what to monitor) */}
      {!step.hypotheses && (step.text || isStreaming) && (
        <div className="px-4 py-3">
          <div className="text-xs text-gray-600 mb-2 uppercase tracking-wider">Agent reasoning</div>
          <StreamingText text={step.text} streaming={step.status === "running"} />
        </div>
      )}

      {/* Loading skeleton — shown before any tool events or text arrive */}
      {step.status === "running" && !step.hypotheses && step.text.length === 0 && step.toolEvents.length === 0 && (
        <div className="px-4 py-3 flex items-center gap-2 text-xs text-gray-500">
          <span className="animate-spin">⟳</span> Waiting for agent...
        </div>
      )}
    </div>
  );
}
