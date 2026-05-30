export type TaskStatus = 'Not Started' | 'In Progress' | 'Completed' | 'Blocked' | 'At Risk'

export type SyncState = 'idle' | 'syncing' | 'error'

export type AppView = 'gantt' | 'kanban'

export interface FirewallTask {
  id: string
  name: string
  status: TaskStatus
  assignee: string
  section: string
  startDate: string | null
  dueDate: string | null
  completed: boolean
  notes?: string
}

export interface Filters {
  section: string
  assignee: string
  status: string
}
