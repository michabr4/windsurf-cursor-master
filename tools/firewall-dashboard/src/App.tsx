import { useState, useEffect, useMemo } from 'react'
import { FirewallTask, Filters, AppView } from './types'
import KPIBar from './components/KPIBar'
import FilterBar from './components/FilterBar'
import GanttView from './components/GanttView'
import KanbanBoard from './components/KanbanBoard'

const DEFAULT_FILTERS: Filters = { section: '', assignee: '', status: '' }

export default function App() {
  const [tasks, setTasks] = useState<FirewallTask[]>([])
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS)
  const [view, setView] = useState<AppView>('gantt')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/data/tasks.json')
      .then(r => r.json())
      .then((data: FirewallTask[]) => {
        setTasks(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = useMemo(
    () =>
      tasks.filter(t => {
        if (filters.section && t.section !== filters.section) return false
        if (filters.assignee && t.assignee !== filters.assignee) return false
        if (filters.status && t.status !== filters.status) return false
        return true
      }),
    [tasks, filters],
  )

  const sections = useMemo(
    () => [...new Set(tasks.map(t => t.section).filter(Boolean))].sort(),
    [tasks],
  )

  const assignees = useMemo(
    () => [...new Set(tasks.map(t => t.assignee).filter(Boolean))].sort(),
    [tasks],
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gray-900 text-white px-6 py-4 shadow">
        <h1 className="text-xl font-semibold tracking-tight">
          Firewall Migration Dashboard
        </h1>
      </header>
      <main className="px-6 py-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-gray-400">
            Loading tasks…
          </div>
        ) : (
          <>
            <KPIBar tasks={filtered} />
            <FilterBar
              filters={filters}
              view={view}
              sections={sections}
              assignees={assignees}
              onFiltersChange={setFilters}
              onViewChange={setView}
            />
            {view === 'gantt' ? (
              <GanttView tasks={filtered} />
            ) : (
              <KanbanBoard tasks={filtered} />
            )}
          </>
        )}
      </main>
    </div>
  )
}
