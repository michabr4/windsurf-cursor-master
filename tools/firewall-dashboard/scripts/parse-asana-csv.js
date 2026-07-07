#!/usr/bin/env node
/**
 * Parse a manually exported Asana CSV and write public/data/tasks.json.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadEnv } from './asana-env.js'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const OUT_PATH = join(ROOT, 'public', 'data', 'tasks.json')
const DEFAULT_CSV = join(ROOT, 'data', 'asana-export.csv')

/** @typedef {'Not Started' | 'In Progress' | 'Completed' | 'Blocked' | 'At Risk'} TaskStatus */

/** @param {string} text */
function parseCsv(text) {
  /** @type {string[][]} */
  const rows = []
  /** @type {string[]} */
  let row = []
  let field = ''
  let inQuotes = false

  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    const next = text[i + 1]

    if (inQuotes) {
      if (c === '"' && next === '"') {
        field += '"'
        i++
      } else if (c === '"') {
        inQuotes = false
      } else {
        field += c
      }
      continue
    }

    if (c === '"') {
      inQuotes = true
    } else if (c === ',') {
      row.push(field)
      field = ''
    } else if (c === '\n' || (c === '\r' && next === '\n')) {
      row.push(field)
      rows.push(row)
      row = []
      field = ''
      if (c === '\r') i++
    } else if (c !== '\r') {
      field += c
    }
  }

  if (field.length > 0 || row.length > 0) {
    row.push(field)
    rows.push(row)
  }

  return rows
}

/** @param {string[]} headers @param {string[]} names */
function columnIndex(headers, names) {
  const normalized = headers.map(h => h.trim().toLowerCase())
  for (const name of names) {
    const idx = normalized.indexOf(name.toLowerCase())
    if (idx >= 0) return idx
  }
  return -1
}

/** @param {string} value */
function parseCompleted(value) {
  const v = (value || '').trim().toLowerCase()
  return v === 'yes' || v === 'true' || v === '1'
}

/** @param {string} raw @param {boolean} completed @returns {TaskStatus} */
function mapStatus(raw, completed) {
  if (completed) return 'Completed'

  const v = (raw || '').trim()
  /** @type {Record<string, TaskStatus>} */
  const map = {
    'Not Started': 'Not Started',
    'In Progress': 'In Progress',
    Completed: 'Completed',
    Done: 'Completed',
    Blocked: 'Blocked',
    'At Risk': 'At Risk',
  }
  if (v && map[v]) return map[v]
  return 'In Progress'
}

/** @param {string | undefined} value */
function dateOrNull(value) {
  const v = (value || '').trim()
  return v || null
}

/** @param {string[]} headers @param {string[]} cells @param {number} rowNum */
function rowToTask(headers, cells, rowNum) {
  const idx = names =>
    columnIndex(headers, names)

  const gidIdx = idx(['Task ID', 'GID', 'gid'])
  const nameIdx = idx(['Name'])
  const assigneeIdx = idx(['Assignee', 'Assignee Name'])
  const dueIdx = idx(['Due Date'])
  const startIdx = idx(['Start Date'])
  const completedIdx = idx(['Completed'])
  const sectionIdx = idx(['Section/Column', 'Section'])
  const statusIdx = idx(['Status'])

  const get = i => (i >= 0 && i < cells.length ? cells[i].trim() : '')

  const completed =
    completedIdx >= 0 ? parseCompleted(get(completedIdx)) : false
  const due = dueIdx >= 0 ? dateOrNull(get(dueIdx)) : null
  const start = startIdx >= 0 ? dateOrNull(get(startIdx)) : null

  return {
    id: gidIdx >= 0 && get(gidIdx) ? get(gidIdx) : String(rowNum),
    name: nameIdx >= 0 ? get(nameIdx) : '',
    section: sectionIdx >= 0 ? get(sectionIdx) : '',
    assignee: assigneeIdx >= 0 && get(assigneeIdx) ? get(assigneeIdx) : 'Unassigned',
    status: mapStatus(statusIdx >= 0 ? get(statusIdx) : '', completed),
    startDate: start || due,
    dueDate: due,
    completed,
  }
}

function main() {
  const env = loadEnv()
  const csvPath = resolve(
    ROOT,
    (env.ASANA_CSV_PATH || './data/asana-export.csv').trim() || DEFAULT_CSV,
  )

  if (!existsSync(csvPath)) {
    console.error(`CSV not found: ${csvPath}`)
    console.error('')
    console.error('Export from Asana: open project → ··· menu → Export → CSV')
    console.error('Save the file and set ASANA_CSV_PATH in .env (default: ./data/asana-export.csv)')
    process.exit(1)
  }

  const text = readFileSync(csvPath, 'utf8').replace(/^\uFEFF/, '')
  const rows = parseCsv(text).filter(r => r.some(c => (c || '').trim()))

  if (rows.length < 2) {
    console.error('CSV has no data rows (need header + at least one task).')
    process.exit(1)
  }

  const headers = rows[0]
  const tasks = rows.slice(1).map((cells, i) => rowToTask(headers, cells, i + 1))

  mkdirSync(dirname(OUT_PATH), { recursive: true })
  writeFileSync(OUT_PATH, `${JSON.stringify(tasks, null, 2)}\n`, 'utf8')
  console.log(`✅ ${tasks.length} tasks written to public/data/tasks.json`)
}

main()
