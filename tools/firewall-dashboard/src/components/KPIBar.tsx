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
    { label: 'Total', value: total, Icon: ListTodo, cls: 'border-blue-200 bg-blue-50 text-blue-700' },
    { label: 'Completed', value: completed, Icon: CheckCircle2, cls: 'border-green-200 bg-green-50 text-green-700' },
    { label: 'In Progress', value: inProgress, Icon: Clock, cls: 'border-yellow-200 bg-yellow-50 text-yellow-700' },
    { label: 'At Risk', value: atRisk, Icon: AlertTriangle, cls: 'border-orange-200 bg-orange-50 text-orange-700' },
    { label: 'Blocked', value: blocked, Icon: XCircle, cls: 'border-red-200 bg-red-50 text-red-700' },
    { label: 'Overdue', value: overdue, Icon: AlertCircle, cls: 'border-purple-200 bg-purple-50 text-purple-700' },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map(({ label, value, Icon, cls }) => (
        <div key={label} className={`rounded-lg border p-4 ${cls}`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{label}</span>
            <Icon className="w-4 h-4 opacity-70" />
          </div>
          <p className="mt-1 text-2xl font-bold">{value}</p>
        </div>
      ))}
    </div>
  )
}
