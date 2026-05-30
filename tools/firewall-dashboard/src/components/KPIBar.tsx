import { CheckCircle2, Clock, AlertTriangle, XCircle, ListTodo, AlertCircle } from 'lucide-react'
import { FirewallTask } from '../types'

interface Props {
  tasks: FirewallTask[]
}

export default function KPIBar({ tasks }: Props) {
  const today = new Date().toISOString().split('T')[0]
  const total = tasks.length
  const completed = tasks.filter(t => t.status === 'Completed').length
  const inProgress = tasks.filter(t => t.status === 'In Progress').length
  const blocked = tasks.filter(t => t.status === 'Blocked').length
  const atRisk = tasks.filter(t => t.status === 'At Risk').length
  const overdue = tasks.filter(
    t => !t.completed && t.dueDate != null && t.dueDate < today,
  ).length

  const cards = [
    { label: 'Total',       value: total,      Icon: ListTodo,      cls: 'border-[#049fd9]/30 bg-[#049fd9]/8 text-[#049fd9]', num: 'text-cisco-dark' },
    { label: 'Completed',   value: completed,  Icon: CheckCircle2,  cls: 'border-[#6cc04a]/30 bg-[#6cc04a]/8 text-[#6cc04a]', num: 'text-cisco-dark' },
    { label: 'In Progress', value: inProgress, Icon: Clock,         cls: 'border-[#00bceb]/30 bg-[#00bceb]/8 text-[#00bceb]', num: 'text-cisco-dark' },
    { label: 'At Risk',     value: atRisk,     Icon: AlertTriangle, cls: 'border-orange-300/50 bg-orange-50 text-orange-600',  num: 'text-slate-800'  },
    { label: 'Blocked',     value: blocked,    Icon: XCircle,       cls: 'border-red-300/50 bg-red-50 text-red-600',           num: 'text-slate-800'  },
    { label: 'Overdue',     value: overdue,    Icon: AlertCircle,   cls: 'border-slate-300 bg-slate-100 text-slate-600',       num: 'text-slate-800'  },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map(({ label, value, Icon, cls, num }) => (
        <div key={label} className={`kpi-card rounded-2xl border bg-white p-4 shadow-sm ${cls}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider opacity-80">{label}</span>
            <Icon className="w-4 h-4 opacity-60" />
          </div>
          <p className={`text-3xl font-black tracking-tight ${num}`}>{value}</p>
        </div>
      ))}
    </div>
  )
}
