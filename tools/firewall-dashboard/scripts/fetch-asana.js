#!/usr/bin/env node
/**
 * Fetch Asana project tasks and write public/data/tasks.json for the dashboard.
 */
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { URLSearchParams } from 'node:url'
import { loadEnv, upsertEnv } from './asana-env.js'

const TOKEN_URL = 'https://app.asana.com/-/oauth_token'
const API_BASE = 'https://app.asana.com/api/1.0'
const OPT_FIELDS =
  'gid,name,assignee.name,due_on,start_on,completed,memberships.section.name,custom_fields.name,custom_fields.display_value,custom_fields.enum_value.name'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const OUT_PATH = join(ROOT, 'public', 'data', 'tasks.json')

/** @typedef {'Not Started' | 'In Progress' | 'Completed' | 'Blocked' | 'At Risk'} TaskStatus */

/** @param {Record<string, string>} form */
async function exchangeToken(form) {
  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(form),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Asana token error ${res.status}: ${text.slice(0, 500)}`)
  }
  const payload = await res.json()
  if (!payload?.access_token) {
    throw new Error('Asana OAuth response missing access_token')
  }
  const updates = { ASANA_ACCESS_TOKEN: payload.access_token }
  if (payload.refresh_token) updates.ASANA_REFRESH_TOKEN = payload.refresh_token
  if (payload.expires_in) {
    updates.ASANA_TOKEN_EXPIRES_AT = String(
      Math.floor(Date.now() / 1000) + Number(payload.expires_in),
    )
  }
  upsertEnv(updates)
  return payload.access_token
}

/** @param {string} token @param {string} url */
async function asanaGet(token, url) {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Asana API ${res.status}: ${text.slice(0, 500)}`)
  }
  return res.json()
}

/** @param {object} task */
function sectionName(task) {
  const memberships = task.memberships
  if (!Array.isArray(memberships) || memberships.length === 0) return ''
  const section = memberships[0]?.section
  return typeof section?.name === 'string' ? section.name : ''
}

/** @param {object} task @returns {TaskStatus} */
function mapStatus(task) {
  if (task.completed) return 'Completed'

  const fields = Array.isArray(task.custom_fields) ? task.custom_fields : []
  const statusField = fields.find(f => f?.name === 'Status')
  const raw =
    statusField?.display_value ||
    statusField?.enum_value?.name ||
    ''

  /** @type {Record<string, TaskStatus>} */
  const map = {
    'Not Started': 'Not Started',
    'In Progress': 'In Progress',
    Completed: 'Completed',
    Done: 'Completed',
    Blocked: 'Blocked',
    'At Risk': 'At Risk',
  }
  if (raw && map[raw]) return map[raw]
  return 'In Progress'
}

/** @param {object} task */
function toFirewallTask(task) {
  const due = task.due_on || null
  const start = task.start_on || due || null
  return {
    id: String(task.gid),
    name: String(task.name || ''),
    section: sectionName(task),
    assignee: task.assignee?.name || 'Unassigned',
    status: mapStatus(task),
    startDate: start,
    dueDate: due,
    completed: Boolean(task.completed),
  }
}

async function getAccessToken(env) {
  const clientId = (env.ASANA_CLIENT_ID || '').trim()
  const clientSecret = (env.ASANA_CLIENT_SECRET || '').trim()
  const refresh = (env.ASANA_REFRESH_TOKEN || '').trim()
  let access = (env.ASANA_ACCESS_TOKEN || '').trim()

  if (clientId && clientSecret && refresh) {
    const expiresRaw = (env.ASANA_TOKEN_EXPIRES_AT || '').trim()
    const expires = expiresRaw ? Number(expiresRaw) : 0
    const now = Math.floor(Date.now() / 1000)
    if (access && expires && now < expires - 120) return access
    return exchangeToken({
      grant_type: 'refresh_token',
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refresh,
    })
  }

  if (access) return access

  throw new Error('Run `npm run setup-oauth` first')
}

async function fetchAllProjectTasks(token, projectGid) {
  /** @type {object[]} */
  const tasks = []
  let offset

  do {
    const params = new URLSearchParams({ opt_fields: OPT_FIELDS, limit: '100' })
    if (offset) params.set('offset', offset)
    const url = `${API_BASE}/projects/${projectGid}/tasks?${params}`
    const page = await asanaGet(token, url)
    if (Array.isArray(page.data)) tasks.push(...page.data)
    offset = page.next_page?.offset
  } while (offset)

  return tasks
}

async function main() {
  const env = loadEnv()
  const projectGid = (env.ASANA_PROJECT_GID || '').trim()
  if (!projectGid) {
    console.error('Missing ASANA_PROJECT_GID in .env')
    process.exit(1)
  }

  const token = await getAccessToken(env)
  const raw = await fetchAllProjectTasks(token, projectGid)
  const mapped = raw.map(toFirewallTask)

  mkdirSync(dirname(OUT_PATH), { recursive: true })
  writeFileSync(OUT_PATH, `${JSON.stringify(mapped, null, 2)}\n`, 'utf8')
  console.log(`✅ ${mapped.length} tasks written to public/data/tasks.json`)
}

main().catch(err => {
  console.error(err instanceof Error ? err.message : err)
  process.exit(1)
})
