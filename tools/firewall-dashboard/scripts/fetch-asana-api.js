#!/usr/bin/env node
/**
 * Fetch tasks from the Asana REST API and write public/data/tasks.json.
 *
 * Auth:    Personal Access Token stored in .env as ASANA_PAT
 *          Generate one at https://app.asana.com/0/my-apps
 * Project: ASANA_PROJECT_GID in .env
 *          Find it in the Asana project URL: app.asana.com/0/<GID>/...
 *
 * Usage:   npm run fetch
 */
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadEnv } from './asana-env.js'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const OUT_PATH = join(ROOT, 'public', 'data', 'tasks.json')
const ASANA_BASE = 'https://app.asana.com/api/1.0'

const OPT_FIELDS = [
  'gid',
  'name',
  'completed',
  'assignee.name',
  'due_on',
  'start_on',
  'notes',
  'memberships.section.name',
  'custom_fields.name',
  'custom_fields.display_value',
].join(',')

/** @typedef {'Not Started' | 'In Progress' | 'Completed' | 'Blocked' | 'At Risk'} TaskStatus */

/** @param {string} raw @param {boolean} completed @returns {TaskStatus} */
function mapStatus(raw, completed) {
  if (completed) return 'Completed'
  const v = (raw || '').trim()
  /** @type {Record<string, TaskStatus>} */
  const map = {
    'Not Started': 'Not Started',
    'In Progress': 'In Progress',
    'Completed':   'Completed',
    'Done':        'Completed',
    'Blocked':     'Blocked',
    'At Risk':     'At Risk',
  }
  return map[v] ?? 'In Progress'
}

/**
 * Map a raw Asana task object to a FirewallTask.
 * @param {Record<string, any>} task
 */
function toFirewallTask(task) {
  const statusField = (task.custom_fields ?? [])
    .find(f => f.name?.toLowerCase() === 'status')
  const statusRaw = statusField?.display_value ?? ''

  return {
    id:        task.gid,
    name:      task.name ?? '',
    section:   task.memberships?.[0]?.section?.name ?? '',
    assignee:  task.assignee?.name ?? 'Unassigned',
    status:    mapStatus(statusRaw, Boolean(task.completed)),
    startDate: task.start_on ?? task.due_on ?? null,
    dueDate:   task.due_on ?? null,
    completed: Boolean(task.completed),
    notes:     task.notes ?? '',
  }
}

/**
 * Fetch all tasks for a project, following Asana pagination cursors.
 * @param {string} pat
 * @param {string} projectGid
 * @returns {Promise<Record<string, any>[]>}
 */
async function fetchAllTasks(pat, projectGid) {
  const tasks = []
  let url = `${ASANA_BASE}/projects/${projectGid}/tasks?opt_fields=${OPT_FIELDS}&limit=100`

  while (url) {
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${pat}`,
        Accept: 'application/json',
      },
    })

    if (!res.ok) {
      const body = await res.text().catch(() => '')
      throw new Error(`Asana API responded ${res.status}: ${body}`)
    }

    const json = await res.json()
    tasks.push(...(json.data ?? []))
    url = json.next_page?.uri ?? null
  }

  return tasks
}

async function main() {
  const env = loadEnv()
  const pat        = (env.ASANA_PAT ?? '').trim()
  const projectGid = (env.ASANA_PROJECT_GID ?? '').trim()

  if (!pat) {
    console.error('❌  ASANA_PAT is not set in .env')
    console.error('    Generate one at https://app.asana.com/0/my-apps')
    process.exit(1)
  }
  if (!projectGid) {
    console.error('❌  ASANA_PROJECT_GID is not set in .env')
    console.error('    Find it in the project URL: app.asana.com/0/<GID>/...')
    process.exit(1)
  }

  console.log(`🔄  Fetching tasks from Asana project ${projectGid}…`)
  const rawTasks = await fetchAllTasks(pat, projectGid)
  const tasks    = rawTasks.filter(t => t.name).map(toFirewallTask)

  mkdirSync(dirname(OUT_PATH), { recursive: true })
  writeFileSync(OUT_PATH, `${JSON.stringify(tasks, null, 2)}\n`, 'utf8')
  console.log(`✅  ${tasks.length} tasks written to public/data/tasks.json`)
}

main().catch(err => {
  console.error('❌ ', err.message)
  process.exit(1)
})
