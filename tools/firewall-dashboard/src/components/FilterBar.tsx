import type { ChangeEvent } from 'react'
import { LayoutList, LayoutGrid } from 'lucide-react'
import { AppView, Filters } from '../types'

interface Props {
  filters: Filters
  view: AppView
  sections: string[]
  assignees: string[]
  onFiltersChange: (f: Filters) => void
  onViewChange: (v: AppView) => void
}

const STATUSES = ['Not Started', 'In Progress', 'At Risk', 'Blocked', 'Completed']

export default function FilterBar({
  filters,
  view,
  sections,
  assignees,
  onFiltersChange,
  onViewChange,
}: Props) {
  const set =
    (key: keyof Filters) =>
    (e: ChangeEvent<HTMLSelectElement>) =>
      onFiltersChange({ ...filters, [key]: e.target.value })

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3">
      <select
        value={filters.section}
        onChange={set('section')}
        className="rounded border border-gray-300 px-3 py-1.5 text-sm"
      >
        <option value="">All Phases</option>
        {sections.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <select
        value={filters.assignee}
        onChange={set('assignee')}
        className="rounded border border-gray-300 px-3 py-1.5 text-sm"
      >
        <option value="">All Assignees</option>
        {assignees.map(a => (
          <option key={a} value={a}>{a}</option>
        ))}
      </select>

      <select
        value={filters.status}
        onChange={set('status')}
        className="rounded border border-gray-300 px-3 py-1.5 text-sm"
      >
        <option value="">All Statuses</option>
        {STATUSES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <div className="ml-auto flex overflow-hidden rounded-lg border border-gray-300">
        <button
          onClick={() => onViewChange('gantt')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-sm ${
            view === 'gantt'
              ? 'bg-gray-900 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-50'
          }`}
        >
          <LayoutList className="h-4 w-4" /> Gantt
        </button>
        <button
          onClick={() => onViewChange('kanban')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-sm ${
            view === 'kanban'
              ? 'bg-gray-900 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-50'
          }`}
        >
          <LayoutGrid className="h-4 w-4" /> Kanban
        </button>
      </div>
    </div>
  )
}
