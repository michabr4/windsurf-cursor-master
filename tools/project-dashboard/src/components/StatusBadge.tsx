interface StatusBadgeProps {
  status: string
}

const statusStyles: Record<string, string> = {
  Stable: 'bg-cisco-green/15 text-green-800 border-cisco-green/40',
  'In Development': 'bg-cisco-teal/15 text-cyan-900 border-cisco-teal/40',
  Blocked: 'bg-red-100 text-red-800 border-red-300',
  Planned: 'bg-slate-100 text-slate-600 border-slate-300',
  'HITL Active': 'bg-cisco-blue/15 text-cisco-blue border-cisco-blue/40',
  Complete: 'bg-green-100 text-green-900 border-green-400',
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const classes = statusStyles[status] ?? 'bg-slate-100 text-slate-700 border-slate-300'

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${classes}`}>
      {status}
    </span>
  )
}
