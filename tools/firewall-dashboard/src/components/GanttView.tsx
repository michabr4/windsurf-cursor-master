import { Gantt, Task as GanttTask, ViewMode as GanttViewMode } from 'gantt-task-react'
import 'gantt-task-react/dist/index.css'
import { FirewallTask } from '../types'

interface Props {
  tasks: FirewallTask[]
}

const STATUS_COLORS: Record<string, string> = {
  Completed:    '#6cc04a',
  'In Progress': '#00bceb',
  Blocked:      '#ef4444',
  'At Risk':    '#f97316',
  'Not Started': '#94a3b8',
}

export default function GanttView({ tasks }: Props) {
  const dated = tasks.filter(t => t.dueDate)

  const sectionNames = Array.from(new Set(dated.map(t => t.section || 'Unsectioned')))

  const ganttTasks: GanttTask[] = []

  for (const section of sectionNames) {
    const members = dated.filter(t => (t.section || 'Unsectioned') === section)

    const starts = members.map(t => new Date((t.startDate || t.dueDate)! + 'T00:00:00').getTime())
    const ends = members.map(t => {
      const e = new Date(t.dueDate! + 'T00:00:00')
      e.setDate(e.getDate() + 1)
      return e.getTime()
    })
    const projEnd = new Date(Math.max(...ends))
    const projStart = new Date(Math.min(...starts))

    ganttTasks.push({
      id: `section::${section}`,
      name: section,
      start: projStart,
      end: projEnd,
      progress: 0,
      type: 'project' as const,
      hideChildren: false,
    })

    for (const t of members) {
      const color = STATUS_COLORS[t.status] ?? '#94a3b8'
      const start = new Date((t.startDate || t.dueDate)! + 'T00:00:00')
      const end = new Date(t.dueDate! + 'T00:00:00')
      end.setDate(end.getDate() + 1)
      ganttTasks.push({
        id: t.id,
        name: t.name,
        start,
        end,
        progress: t.status === 'Completed' ? 100 : t.status === 'In Progress' ? 50 : 0,
        type: 'task' as const,
        project: `section::${section}`,
        styles: { progressColor: color, progressSelectedColor: color },
      })
    }
  }

  if (ganttTasks.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500 shadow-sm">
        No tasks with due dates to display in Gantt view.
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <Gantt
        tasks={ganttTasks}
        viewMode={GanttViewMode.Week}
        listCellWidth="200px"
        todayColor="rgba(4,159,217,0.12)"
      />
    </div>
  )
}
