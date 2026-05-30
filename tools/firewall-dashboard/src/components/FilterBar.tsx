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
    <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      <select
        title="Filter by phase"
        value={filters.section}
        onChange={set('section')}
        className="rounded-lg border border-slate-300 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 focus:border-[#049fd9] focus:outline-none focus:ring-1 focus:ring-[#049fd9]"
      >
        <option value="">All Phases</option>
        {sections.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <select
        title="Filter by assignee"
        value={filters.assignee}
        onChange={set('assignee')}
        className="rounded-lg border border-slate-300 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 focus:border-[#049fd9] focus:outline-none focus:ring-1 focus:ring-[#049fd9]"
      >
        <option value="">All Assignees</option>
        {assignees.map(a => (
          <option key={a} value={a}>{a}</option>
        ))}
      </select>

      <select
        title="Filter by status"
        value={filters.status}
        onChange={set('status')}
        className="rounded-lg border border-slate-300 bg-slate-50 px-3 py-1.5 text-sm text-slate-700 focus:border-[#049fd9] focus:outline-none focus:ring-1 focus:ring-[#049fd9]"
      >
        <option value="">All Statuses</option>
        {STATUSES.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      <div className="ml-auto flex overflow-hidden rounded-xl border border-slate-300">
        <button
          onClick={() => onViewChange('gantt')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium transition-colors ${
            view === 'gantt'
              ? 'bg-[#049fd9] text-white'
              : 'bg-white text-slate-600 hover:bg-slate-50'
          }`}
        >
          <LayoutList className="h-4 w-4" /> Gantt
        </button>
        <button
          onClick={() => onViewChange('kanban')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium transition-colors ${
            view === 'kanban'
              ? 'bg-[#049fd9] text-white'
              : 'bg-white text-slate-600 hover:bg-slate-50'
          }`}
        >
          <LayoutGrid className="h-4 w-4" /> Kanban
        </button>
      </div>
    </div>
  )
}
