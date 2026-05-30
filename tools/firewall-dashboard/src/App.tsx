import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { FirewallTask, Filters, AppView, SyncState } from './types'
import KPIBar from './components/KPIBar'
import FilterBar from './components/FilterBar'
import GanttView from './components/GanttView'
import KanbanBoard from './components/KanbanBoard'

const DEFAULT_FILTERS: Filters = { section: '', assignee: '', status: '' }
const POLL_INTERVAL_MS = 5 * 60 * 1000

export default function App() {
  const [tasks, setTasks] = useState<FirewallTask[]>([])
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS)
  const [view, setView] = useState<AppView>('gantt')
  const [loading, setLoading] = useState(true)
  const [syncState, setSyncState] = useState<SyncState>('idle')

  const tasksRef = useRef<FirewallTask[]>([])
  useEffect(() => { tasksRef.current = tasks }, [tasks])

  useEffect(() => {
    fetch('/api/tasks')
      .then(r => r.json())
      .then((data: FirewallTask[]) => {
        setTasks(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    const id = setInterval(() => {
      fetch('/api/tasks')
        .then(r => r.json())
        .then((data: FirewallTask[]) => setTasks(data))
        .catch(() => {})
    }, POLL_INTERVAL_MS)
    return () => clearInterval(id)
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

  const handleTasksChange = useCallback((updated: FirewallTask[]) => {
    const prev = tasksRef.current
    setTasks(updated)
    updated.forEach(task => {
      const old = prev.find(p => p.id === task.id)
      if (!old) return
      const changes: Partial<FirewallTask> = {}
      if (old.status !== task.status) changes.status = task.status
      if (old.completed !== task.completed) changes.completed = task.completed
      if (Object.keys(changes).length === 0) return
      fetch(`/api/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(changes),
      }).catch(console.error)
    })
  }, [])

  const handleSync = useCallback(async () => {
    setSyncState('syncing')
    try {
      await fetch('/api/tasks/sync', { method: 'POST' })
      const data: FirewallTask[] = await fetch('/api/tasks').then(r => r.json())
      setTasks(data)
      setSyncState('idle')
    } catch {
      setSyncState('error')
      setTimeout(() => setSyncState('idle'), 3000)
    }
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased">
      <header className="cisco-header text-white px-6 py-5 shadow-lg">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold tracking-widest uppercase text-cisco-sky/70 mb-0.5">
              Cisco CX
            </p>
            <h1 className="text-xl font-bold tracking-tight">
              Firewall Migration Dashboard
            </h1>
          </div>
          <button
            onClick={handleSync}
            disabled={syncState === 'syncing'}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all select-none ${
              syncState === 'syncing'
                ? 'bg-white/10 text-white/50 cursor-not-allowed'
                : syncState === 'error'
                ? 'bg-red-500/80 text-white'
                : 'bg-white/15 hover:bg-white/25 text-white cursor-pointer'
            }`}
          >
            <span className={syncState === 'syncing' ? 'animate-spin inline-block' : ''}>
              ↻
            </span>
            {syncState === 'syncing' ? 'Syncing…' : syncState === 'error' ? 'Sync failed' : 'Sync Asana'}
          </button>
        </div>
      </header>
      <main className="max-w-screen-2xl mx-auto px-6 py-5 space-y-4 fade-in-up">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-slate-400">
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
              <KanbanBoard tasks={tasks} onTasksChange={handleTasksChange} />
            )}
          </>
        )}
      </main>
    </div>
  )
}
