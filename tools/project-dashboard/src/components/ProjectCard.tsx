import { Calendar } from 'lucide-react'
import { useState } from 'react'
import type { Project } from '../types/project'
import ProgressRing from './ProgressRing'
import StatusBadge from './StatusBadge'

interface ProjectCardProps {
  project: Project
}

const categoryStyles: Record<string, string> = {
  Platform: 'bg-cisco-blue/10 text-cisco-blue',
  'AI Agent': 'bg-cisco-teal/10 text-cyan-800',
  Bot: 'bg-orange-100 text-orange-800',
  Agent: 'bg-purple-100 text-purple-800',
  Tool: 'bg-slate-200 text-slate-700',
}

const trustTierStyles: Record<string, string> = {
  T1: 'bg-cisco-green text-white',
  T2: 'bg-cisco-blue text-white',
  T3: 'bg-cisco-navy text-white',
}

export default function ProjectCard({ project }: ProjectCardProps) {
  const [expanded, setExpanded] = useState(false)
  const etaIsTbd = project.eta.toLowerCase().includes('tbd')

  return (
    <article className="fade-in-up flex flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-lg font-bold text-slate-900">{project.name}</h3>
          <p className="mt-1 text-xs text-slate-500">{project.location}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={project.status} />
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${categoryStyles[project.category] ?? 'bg-slate-100 text-slate-600'}`}>
            {project.category}
          </span>
          {project.trustTier && (
            <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${trustTierStyles[project.trustTier]}`}>
              {project.trustTier}
            </span>
          )}
        </div>
      </div>

      <div className="mb-4 flex items-center gap-4">
        <ProgressRing pct={project.progressPct} />
        <div>
          <p className="text-sm font-medium text-slate-700">{project.phase}</p>
          <p className="text-xs text-slate-500">Updated {project.lastUpdated}</p>
        </div>
      </div>

      <div className={`mb-3 flex items-center gap-2 text-sm ${etaIsTbd ? 'text-orange-600' : 'text-slate-700'}`}>
        <Calendar className="h-4 w-4 shrink-0" />
        <span className="font-medium">ETA:</span>
        <span>{project.eta}</span>
      </div>

      {project.blockers.length > 0 && (
        <div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-red-700">Blockers</p>
          <ul className="space-y-1 text-sm text-red-800">
            {project.blockers.map((blocker) => (
              <li key={blocker}>• {blocker}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="mb-3 text-left text-sm font-medium text-cisco-blue hover:underline"
      >
        {expanded ? 'Hide details' : 'Show completed / remaining'}
      </button>

      {expanded && (
        <div className="mb-3 grid gap-3 sm:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-semibold uppercase text-cisco-green">Completed</p>
            <ul className="space-y-1 text-sm text-slate-700">
              {project.completedItems.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold uppercase text-slate-500">Remaining</p>
            <ul className="space-y-1 text-sm text-slate-700">
              {project.remainingItems.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <p className="mt-auto border-t border-slate-100 pt-3 text-sm italic text-slate-600">
        {project.expectedOutcome}
      </p>
    </article>
  )
}
