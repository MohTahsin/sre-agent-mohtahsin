/**
 * ApprovalGate — shown between step 1 (analysis) and step 2 (remediation).
 *
 * Displays what the agent proposes to do and requires explicit human sign-off
 * before the AWS API call is made.
 */
export default function ApprovalGate({ step, onApprove, onReject }) {
  return (
    <div className="rounded-lg border border-brand-yellow/50 bg-yellow-950/20 animate-slide-in overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-brand-yellow/30 bg-yellow-900/10">
        <span className="text-lg">⚠️</span>
        <div className="flex-1">
          <p className="text-sm font-semibold text-brand-yellow">Human Approval Required</p>
          <p className="text-xs text-gray-500 mt-0.5">
            The agent wants to execute a production AWS action. Review and approve before proceeding.
          </p>
        </div>
        <span className="text-xs px-2 py-1 rounded bg-yellow-900/40 border border-brand-yellow/30 text-brand-yellow font-semibold">
          AWAITING APPROVAL
        </span>
      </div>

      {/* Proposed action */}
      <div className="px-4 py-4 space-y-3">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Proposed Action</p>
          <div className="bg-surface-0 rounded-lg border border-surface-3 p-3 space-y-2 text-sm">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32 text-xs shrink-0">Tool</span>
              <code className="text-brand-purple">increase_lambda_concurrency()</code>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32 text-xs shrink-0">Function</span>
              <code className="text-brand-blue">payments-processor-prod</code>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32 text-xs shrink-0">Change</span>
              <span>
                Reserved concurrency{" "}
                <span className="text-brand-red font-semibold">10</span>
                {" → "}
                <span className="text-brand-green font-semibold">20</span>
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32 text-xs shrink-0">Environment</span>
              <span className="text-brand-orange">Production (us-east-1)</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32 text-xs shrink-0">AWS API</span>
              <code className="text-xs text-gray-400">lambda:PutFunctionConcurrency</code>
            </div>
          </div>
        </div>

        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Rationale</p>
          <p className="text-xs text-gray-400 leading-relaxed">
            Based on log analysis, the most likely root cause is that the reserved concurrency limit
            of <span className="text-brand-red">10</span> is insufficient for current peak traffic.
            Increasing to <span className="text-brand-green">20</span> will allow more concurrent
            executions and reduce the <code className="text-brand-orange">TooManyRequestsException</code> error
            rate immediately. This is a non-destructive, instantly reversible change.
          </p>
        </div>
      </div>

      {/* Action buttons — Approve triggers POST /api/approve-remediation; Reject is client-side only. */}
      <div className="flex items-center gap-3 px-4 py-3 border-t border-surface-3/60 bg-surface-0/30">
        <button
          onClick={onApprove}
          className="px-5 py-2 rounded bg-brand-green hover:bg-green-400 text-black text-sm font-semibold transition-colors shadow"
        >
          ✓ Approve Remediation
        </button>
        <button
          onClick={onReject}
          className="px-4 py-2 rounded bg-surface-2 hover:bg-surface-3 text-gray-400 hover:text-gray-200 text-sm transition-colors border border-surface-3"
        >
          ✕ Reject
        </button>
        <span className="text-xs text-gray-600 ml-auto">
          This action will modify production infrastructure.
        </span>
      </div>
    </div>
  );
}
