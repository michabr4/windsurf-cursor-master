import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const phases = [
  {
    phase: 'Phase 0',
    label: 'Ops & Baselines',
    status: 'complete',
    agents: 0,
    fill: '#6cc04a',
    detail: 'Ops blockers and workflow baselines — exit when tokens rotated and MCP access confirmed.',
  },
  {
    phase: 'Phase 1',
    label: 'SDM Pilots',
    status: 'in_progress',
    agents: 3,
    fill: '#00bceb',
    detail: 'Delivery Tracker, Risk Sentinel, Business Review Generator — HITL windows Weeks 8–10.',
  },
  {
    phase: 'Phase 2',
    label: 'Platform Scale',
    status: 'planned',
    agents: 8,
    fill: '#94a3b8',
    detail: 'Bot fixes, Flerken upgrade, Helix publish — target after Phase 1 stable.',
  },
  {
    phase: 'Phase 3',
    label: 'Tools & Workbench',
    status: 'planned',
    agents: 4,
    fill: '#94a3b8',
    detail: 'Firewall dashboard extensions, delivery workbench daily driver.',
  },
  {
    phase: 'Phase 4',
    label: 'Integrations',
    status: 'planned',
    agents: 6,
    fill: '#94a3b8',
    detail: 'Live Salesforce/ServiceNow, GitHub Pages, mobile persistence.',
  },
  {
    phase: 'Phase 5',
    label: 'Agent Chains',
    status: 'planned',
    agents: 5,
    fill: '#94a3b8',
    detail: 'End-to-end workflow automation across CX roles.',
  },
  {
    phase: 'Phase 6',
    label: 'Autonomy',
    status: 'planned',
    agents: 8,
    fill: '#94a3b8',
    detail: 'T3 autonomous chains — Year 2 Q2+ target.',
  },
]

export default function PhaseTimeline() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">AI Factory Phase Timeline</h2>
          <p className="text-sm text-slate-500">Six phases from ops readiness through autonomous agent chains</p>
        </div>
        <div className="hidden items-center gap-2 text-xs text-slate-500 md:flex">
          <span className="inline-block h-3 w-3 rounded bg-cisco-green" /> Complete
          <span className="inline-block h-3 w-3 rounded bg-cisco-teal" /> In progress
          <span className="inline-block h-3 w-3 rounded bg-slate-400" /> Planned
        </div>
      </div>

      <div className="relative h-72 w-full">
        <div
          className="pointer-events-none absolute bottom-12 top-8 z-10 w-0.5 bg-cisco-blue"
          style={{ left: '38%' }}
          title="Current date marker"
        />
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={phases} layout="vertical" margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[0, 10]} hide />
            <YAxis type="category" dataKey="phase" width={72} tick={{ fontSize: 12 }} />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const row = payload[0].payload as (typeof phases)[number]
                return (
                  <div className="max-w-xs rounded-lg border border-slate-200 bg-white p-3 text-sm shadow-lg">
                    <p className="font-semibold text-slate-900">{row.label}</p>
                    <p className="mt-1 capitalize text-slate-600">Status: {row.status.replace('_', ' ')}</p>
                    <p className="text-slate-600">Agents: {row.agents || 'Ops only'}</p>
                    <p className="mt-2 text-slate-700">{row.detail}</p>
                  </div>
                )
              }}
            />
            <Bar dataKey="agents" radius={[0, 6, 6, 0]} barSize={22}>
              {phases.map((entry) => (
                <Cell key={entry.phase} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
