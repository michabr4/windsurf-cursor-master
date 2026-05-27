import { Gantt, Task as GanttTask, ViewMode as GanttViewMode } from 'gantt-task-react'
import 'gantt-task-react/dist/index.css'
import { FirewallTask } from '../types'

interface Props {
  tasks: FirewallTask[]
}

const STATUS_COLORS: Record<string, string> = {
  Completed: '#22c55e',
  'In Progress': '#f59e0b',
  Blocked: '#ef4444',
  'At Risk': '#f97316',
  'Not Started': '#94a3b8',
}

export default function GanttView({ tasks }: Props) {
  const ganttTasks: GanttTask[] = tasks
    .filter(t => t.startDate && t.dueDate && t.startDate < t.dueDate)
    .map(t => {
      const color = STATUS_COLORS[t.status] ?? '#94a3b8'
      const end = new Date(t.dueDate! + 'T00:00:00')
      end.setDate(end.getDate() + 1)
      return {
        id: t.id,
        name: t.name,
        start: new Date(t.startDate! + 'T00:00:00'),
        end,
        progress: t.status === 'Completed' ? 100 : t.status === 'In Progress' ? 50 : 0,
        type: 'task' as const,
        styles: { progressColor: color, progressSelectedColor: color },
      }
    })

  if (ganttTasks.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">
        No tasks with start &amp; due dates to display in Gantt view.
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <Gantt
        tasks={ganttTasks}
        viewMode={GanttViewMode.Week}
        listCellWidth="180px"
        todayColor="rgba(59,130,246,0.1)"
      />
    </div>
  )
}
