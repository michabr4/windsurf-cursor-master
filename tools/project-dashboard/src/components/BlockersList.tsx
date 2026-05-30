import type { OpsBlocker } from '../types/project'

interface BlockersListProps {
  blockers: OpsBlocker[]
}

const priorityOrder: Record<OpsBlocker['priority'], number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
}

const priorityStyles: Record<OpsBlocker['priority'], string> = {
  CRITICAL: 'bg-red-600 text-white',
  HIGH: 'bg-orange-500 text-white',
  MEDIUM: 'bg-amber-400 text-slate-900',
  LOW: 'bg-slate-300 text-slate-800',
}

const fixInstructions: Record<string, string> = {
  'webex-bot-token': 'Regenerate bot token at developer.webex.com and update GitHub Secrets.',
  'webex-access-token': 'Run oauth_refresh.py and update WEBEX_ACCESS_TOKEN in GitHub Secrets.',
  'webex-client-secret': 'Paste the new client secret from 2026-05-28 rotation into GitHub Secrets.',
  'azure-ad-registration': 'Register the app in Microsoft Entra admin center and configure redirect URIs.',
  'salesforce-mcp': 'Confirm delegated read access for the Salesforce MCP integration.',
  'servicenow-mcp': 'Confirm ServiceNow MCP credentials and scoped permissions.',
}

export default function BlockersList({ blockers }: BlockersListProps) {
  const pending = blockers
    .filter((blocker) => !blocker.done)
    .sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])

  if (pending.length === 0) {
    return (
      <section className="rounded-xl border border-green-200 bg-green-50 p-4 text-green-800">
        All ops blockers resolved.
      </section>
    )
  }

  return (
    <section className="rounded-xl border border-orange-300 border-t-4 border-t-red-500 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-bold text-slate-900">⚠️ Action Required — Ops Blockers</h2>
      <div className="space-y-3">
        {pending.map((blocker) => (
          <div key={blocker.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className={`rounded px-2 py-0.5 text-xs font-bold ${priorityStyles[blocker.priority]}`}>
                {blocker.priority}
              </span>
              <h3 className="font-semibold text-slate-900">{blocker.title}</h3>
              <span className="text-xs text-slate-500">Owner: {blocker.owner}</span>
            </div>
            <p className="mb-2 text-sm text-slate-700">
              {fixInstructions[blocker.id] ?? 'Complete the required ops step to unblock affected projects.'}
            </p>
            <p className="text-xs text-slate-500">
              Affects: {blocker.affectsProjects.join(', ')}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
