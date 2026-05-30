#!/usr/bin/env node
/**
 * Local Asana proxy API server for the firewall dashboard.
 * Runs on port 3001; Vite proxies /api/* here during `npm run dev:full`.
 *
 * Routes:
 *   GET  /api/tasks        — fetch from Asana (5-min cache) or fallback to tasks.json
 *   PATCH /api/tasks/:id   — push field changes to Asana + update local cache
 *   POST /api/tasks/sync   — force-refresh cache from Asana
 *
 * Auth: ASANA_PAT + ASANA_PROJECT_GID in .env
 * Degrades gracefully to local tasks.json when Asana is unreachable (e.g. Cisco network).
 */
import { createServer } from 'node:http'
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadEnv } from './asana-env.js'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const TASKS_FILE = join(ROOT, 'public', 'data', 'tasks.json')
const PORT = Number(process.env.API_PORT ?? 3001)
const CACHE_TTL_MS = 5 * 60 * 1000
const ASANA_BASE = 'https://app.asana.com/api/1.0'

const OPT_FIELDS = [
  'gid', 'name', 'completed',
  'assignee.name', 'assignee.gid',
  'due_on', 'start_on', 'notes',
  'memberships.section.name',
  'custom_fields.gid', 'custom_fields.name', 'custom_fields.display_value',
].join(',')

// ─── In-memory cache ──────────────────────────────────────────────────────────
/** @type {{ tasks: any[]; ts: number } | null} */
let cache = null

// ─── Asana field helpers ──────────────────────────────────────────────────────
/** @param {string} raw @param {boolean} completed */
function mapStatus(raw, completed) {
  if (completed) return 'Completed'
  const map = {
    'Not Started': 'Not Started',
    'In Progress': 'In Progress',
    'Completed':   'Completed',
    'Done':        'Completed',
    'Blocked':     'Blocked',
    'At Risk':     'At Risk',
  }
  return map[(raw ?? '').trim()] ?? 'In Progress'
}

/** @param {Record<string, any>} task */
function toFirewallTask(task) {
  const statusField = (task.custom_fields ?? []).find(
    f => f.name?.toLowerCase() === 'status',
  )
  return {
    id:        task.gid,
    name:      task.name ?? '',
    section:   task.memberships?.[0]?.section?.name ?? '',
    assignee:  task.assignee?.name ?? 'Unassigned',
    status:    mapStatus(statusField?.display_value ?? '', Boolean(task.completed)),
    startDate: task.start_on ?? task.due_on ?? null,
    dueDate:   task.due_on ?? null,
    completed: Boolean(task.completed),
    notes:     task.notes ?? '',
  }
}

// ─── Asana REST calls ─────────────────────────────────────────────────────────
/**
 * @param {string} pat
 * @param {string} projectGid
 * @returns {Promise<any[]>}
 */
async function fetchAllTasks(pat, projectGid) {
  const tasks = []
  let url = `${ASANA_BASE}/projects/${projectGid}/tasks?opt_fields=${OPT_FIELDS}&limit=100`
  while (url) {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${pat}`, Accept: 'application/json' },
    })
    if (!res.ok) {
      const body = await res.text().catch(() => '')
      throw new Error(`Asana ${res.status}: ${body.slice(0, 300)}`)
    }
    const json = await res.json()
    tasks.push(...(json.data ?? []))
    url = json.next_page?.uri ?? null
  }
  return tasks
}

/**
 * @param {string} pat
 * @param {string} taskGid
 * @param {Record<string, any>} fields   — Asana-native field names
 */
async function patchAsanaTask(pat, taskGid, fields) {
  const res = await fetch(`${ASANA_BASE}/tasks/${taskGid}`, {
    method: 'PUT',
    headers: {
      Authorization:   `Bearer ${pat}`,
      'Content-Type':  'application/json',
      Accept:          'application/json',
    },
    body: JSON.stringify({ data: fields }),
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`Asana PUT ${taskGid} → ${res.status}: ${body.slice(0, 300)}`)
  }
  return res.json()
}

// ─── HTTP helpers ─────────────────────────────────────────────────────────────
/** @param {import('node:http').IncomingMessage} req */
function readBody(req) {
  return new Promise((resolve, reject) => {
    let raw = ''
    req.on('data', chunk => { raw += chunk.toString() })
    req.on('end', () => {
      try { resolve(JSON.parse(raw || 'null')) }
      catch { reject(new Error('Invalid JSON body')) }
    })
    req.on('error', reject)
  })
}

/**
 * @param {import('node:http').ServerResponse} res
 * @param {number} status
 * @param {unknown} data
 */
function send(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json' })
  res.end(JSON.stringify(data))
}

// ─── Route handlers ───────────────────────────────────────────────────────────
async function handleGetTasks(req, res, { pat, projectGid }) {
  if (cache && Date.now() - cache.ts < CACHE_TTL_MS) {
    console.log(`[api] GET /tasks → cache hit (${cache.tasks.length} tasks)`)
    return send(res, 200, cache.tasks)
  }

  if (pat && projectGid) {
    try {
      const raw = await fetchAllTasks(pat, projectGid)
      const tasks = raw.filter(t => t.name).map(toFirewallTask)
      cache = { tasks, ts: Date.now() }
      mkdirSync(dirname(TASKS_FILE), { recursive: true })
      writeFileSync(TASKS_FILE, JSON.stringify(tasks, null, 2) + '\n', 'utf8')
      console.log(`[api] GET /tasks → Asana (${tasks.length} tasks cached)`)
      return send(res, 200, tasks)
    } catch (err) {
      console.warn('[api] Asana unreachable — falling back to tasks.json:', err.message)
    }
  }

  try {
    const data = JSON.parse(readFileSync(TASKS_FILE, 'utf8'))
    if (!cache) cache = { tasks: data, ts: Date.now() }
    console.log(`[api] GET /tasks → local file (${data.length} tasks)`)
    return send(res, 200, data)
  } catch {
    return send(res, 200, [])
  }
}

async function handleSync(req, res, { pat, projectGid }) {
  if (!pat || !projectGid) {
    return send(res, 400, { error: 'ASANA_PAT or ASANA_PROJECT_GID not set in .env' })
  }
  cache = null
  try {
    const raw = await fetchAllTasks(pat, projectGid)
    const tasks = raw.filter(t => t.name).map(toFirewallTask)
    cache = { tasks, ts: Date.now() }
    mkdirSync(dirname(TASKS_FILE), { recursive: true })
    writeFileSync(TASKS_FILE, JSON.stringify(tasks, null, 2) + '\n', 'utf8')
    console.log(`[api] POST /tasks/sync → ${tasks.length} tasks written`)
    return send(res, 200, { ok: true, count: tasks.length })
  } catch (err) {
    console.error('[api] Sync failed:', err.message)
    return send(res, 502, { error: err.message })
  }
}

async function handlePatchTask(req, res, taskGid, { pat }) {
  let body
  try {
    body = await readBody(req)
  } catch {
    return send(res, 400, { error: 'Invalid JSON body' })
  }

  // Optimistic: update local cache immediately
  if (cache) {
    cache.tasks = cache.tasks.map(t => t.id === taskGid ? { ...t, ...body } : t)
  }

  if (!pat) {
    console.log(`[api] PATCH /tasks/${taskGid} → local only (no PAT)`)
    return send(res, 200, { ok: true, asana: false, reason: 'no PAT configured' })
  }

  // Map dashboard fields → Asana API field names
  const asanaFields = {}
  if ('completed' in body) asanaFields.completed = body.completed
  // status → map to completed boolean (custom field write requires field GID discovery)
  if ('status' in body) asanaFields.completed = body.status === 'Completed'
  if ('dueDate' in body) asanaFields.due_on = body.dueDate ?? null
  if ('startDate' in body) asanaFields.start_on = body.startDate ?? null
  if ('notes' in body) asanaFields.notes = body.notes

  if (Object.keys(asanaFields).length === 0) {
    return send(res, 200, { ok: true, asana: false, reason: 'no Asana-writable fields' })
  }

  try {
    await patchAsanaTask(pat, taskGid, asanaFields)
    console.log(`[api] PATCH /tasks/${taskGid} → Asana`, asanaFields)
    return send(res, 200, { ok: true, asana: true })
  } catch (err) {
    console.error(`[api] Asana PATCH failed for ${taskGid}:`, err.message)
    // Cache already updated optimistically — caller decides whether to rollback
    return send(res, 502, { error: err.message, asana: false })
  }
}

// ─── Server ───────────────────────────────────────────────────────────────────
const server = createServer(async (req, res) => {
  // CORS for local dev (Vite proxy handles this in production-like dev mode)
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:5173')
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PATCH,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    res.writeHead(204)
    res.end()
    return
  }

  const env = loadEnv()
  const ctx = {
    pat:        (env.ASANA_PAT ?? '').trim(),
    projectGid: (env.ASANA_PROJECT_GID ?? '').trim(),
  }

  const url    = (req.url ?? '').split('?')[0]
  const method = req.method ?? 'GET'

  try {
    if (method === 'GET'  && url === '/api/tasks')         return await handleGetTasks(req, res, ctx)
    if (method === 'POST' && url === '/api/tasks/sync')    return await handleSync(req, res, ctx)
    if (method === 'PATCH' && url.startsWith('/api/tasks/')) {
      const taskGid = url.slice('/api/tasks/'.length)
      if (taskGid) return await handlePatchTask(req, res, taskGid, ctx)
    }
    send(res, 404, { error: 'not found' })
  } catch (err) {
    console.error('[api] Unhandled error:', err)
    send(res, 500, { error: err.message })
  }
})

server.listen(PORT, () => {
  const env = loadEnv()
  const hasPat = Boolean((env.ASANA_PAT ?? '').trim())
  const hasGid = Boolean((env.ASANA_PROJECT_GID ?? '').trim())
  console.log(`\n🔌  Asana proxy API  →  http://localhost:${PORT}`)
  console.log(`    GET  /api/tasks        (5-min cache)`)
  console.log(`    PATCH /api/tasks/:id   (write-back)`)
  console.log(`    POST /api/tasks/sync   (force refresh)`)
  console.log(`\n    PAT configured: ${hasPat ? '✅' : '❌  set ASANA_PAT in .env'}`)
  console.log(`    Project GID:    ${hasGid ? '✅' : '❌  set ASANA_PROJECT_GID in .env'}\n`)
})
