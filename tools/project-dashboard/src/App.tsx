import projectData from './data/projects.json'
import type { ProjectData } from './types/project'
import BlockersList from './components/BlockersList'
import Header from './components/Header'
import PhaseTimeline from './components/PhaseTimeline'
import ProjectCard from './components/ProjectCard'
import SummaryBar from './components/SummaryBar'
import StatusBadge from './components/StatusBadge'

const data = projectData as ProjectData

const legend = [
  { status: 'Stable', color: 'bg-cisco-green' },
  { status: 'In Development', color: 'bg-cisco-teal' },
  { status: 'Blocked', color: 'bg-red-500' },
  { status: 'Planned', color: 'bg-slate-400' },
  { status: 'HITL Active', color: 'bg-cisco-blue' },
  { status: 'Complete', color: 'bg-green-700' },
]

export default function App() {
  const pendingOpsCount = data.opsBlockers.filter((blocker) => !blocker.done).length

  return (
    <div className="min-h-screen bg-slate-50">
      <Header lastUpdated={data.lastUpdated} />

      <main className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6">
        <SummaryBar summary={data.summary} pendingOpsCount={pendingOpsCount} />
        <BlockersList blockers={data.opsBlockers} />

        <section>
          <h2 className="mb-4 text-xl font-bold text-slate-900">Active Projects</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
            {data.projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        </section>

        <PhaseTimeline />

        <footer className="rounded-xl border border-slate-200 bg-white p-4">
          <p className="mb-3 text-sm font-semibold text-slate-700">Status Legend</p>
          <div className="flex flex-wrap gap-3">
            {legend.map((item) => (
              <div key={item.status} className="flex items-center gap-2">
                <StatusBadge status={item.status} />
              </div>
            ))}
          </div>
        </footer>
      </main>
    </div>
  )
}
