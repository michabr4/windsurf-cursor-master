import { FirewallTask, TaskStatus } from '../types'

interface Props {
  tasks: FirewallTask[]
}

const COLUMNS: TaskStatus[] = ['Not Started', 'In Progress', 'At Risk', 'Blocked', 'Completed']

const TOP_BORDER: Record<TaskStatus, string> = {
  'Not Started': 'border-t-gray-400',
  'In Progress': 'border-t-yellow-400',
  'At Risk': 'border-t-orange-400',
  'Blocked': 'border-t-red-400',
  'Completed': 'border-t-green-400',
}

export default function KanbanBoard({ tasks }: Props) {
  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {COLUMNS.map(status => {
        const col = tasks.filter(t => t.status === status)
        return (
          <div
            key={status}
            className={`flex-none w-64 rounded-lg border border-gray-200 border-t-4 bg-white ${TOP_BORDER[status]}`}
          >
            <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
              <span className="text-sm font-medium text-gray-700">{status}</span>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                {col.length}
              </span>
            </div>
            <div className="max-h-[60vh] overflow-y-auto space-y-2 p-3">
              {col.length === 0 ? (
                <p className="py-4 text-center text-xs text-gray-400">No tasks</p>
              ) : (
                col.map(task => (
                  <div
                    key={task.id}
                    className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm transition-shadow hover:shadow-md"
                  >
                    <p className="text-sm font-medium leading-snug text-gray-800">{task.name}</p>
                    {task.section && (
                      <p className="mt-0.5 text-xs text-gray-500">{task.section}</p>
                    )}
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-gray-400">
                        {task.assignee || 'Unassigned'}
                      </span>
                      {task.dueDate && (
                        <span className="text-xs text-gray-400">{task.dueDate}</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
