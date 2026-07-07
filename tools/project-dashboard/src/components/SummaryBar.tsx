import type { ProjectData } from '../types/project'

interface SummaryBarProps {
  summary: ProjectData['summary']
  pendingOpsCount: number
}

interface KpiCardProps {
  label: string
  value: number | string
  accent?: string
}

function KpiCard({ label, value, accent = 'text-slate-900' }: KpiCardProps) {
  return (
    <div className="kpi-card rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-1 text-3xl font-bold ${accent}`}>{value}</p>
    </div>
  )
}

export default function SummaryBar({ summary, pendingOpsCount }: SummaryBarProps) {
  return (
    <section className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
      <KpiCard label="Total Projects" value={summary.total} />
      <KpiCard label="On Track" value={summary.onTrack} accent="text-cisco-green" />
      <KpiCard label="Blocked" value={summary.blocked} accent="text-red-600" />
      <KpiCard label="Stable" value={summary.stable} accent="text-cisco-teal" />
      <KpiCard
        label="Phase 0 Ops Pending"
        value={pendingOpsCount}
        accent="text-orange-600"
      />
    </section>
  )
}
