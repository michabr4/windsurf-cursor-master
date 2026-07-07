export interface Project {
  id: string
  name: string
  category: 'Platform' | 'AI Agent' | 'Bot' | 'Agent' | 'Tool'
  location: string
  status: 'Stable' | 'In Development' | 'Blocked' | 'Planned' | 'HITL Active' | 'Complete'
  phase: string
  phase_number: number
  progressPct: number
  lastUpdated: string
  eta: string
  blockers: string[]
  completedItems: string[]
  remainingItems: string[]
  expectedOutcome: string
  trustTier: 'T1' | 'T2' | 'T3' | null
}

export interface OpsBlocker {
  id: string
  title: string
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  owner: string
  done: boolean
  affectsProjects: string[]
}

export interface ProjectData {
  lastUpdated: string
  summary: {
    total: number
    onTrack: number
    blocked: number
    stable: number
    plannedAgents: number
  }
  projects: Project[]
  opsBlockers: OpsBlocker[]
}
