import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
export const ENV_PATH = join(ROOT, '.env')

/** @param {string} [path] */
export function loadEnv(path = ENV_PATH) {
  const env = { ...process.env }
  if (!existsSync(path)) return env
  for (const line of readFileSync(path, 'utf8').split(/\r?\n/)) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eq = line.indexOf('=')
    if (eq === -1) continue
    const key = line.slice(0, eq).trim()
    let value = line.slice(eq + 1).trim()
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }
    env[key] = value
  }
  return env
}

/** @param {Record<string, string>} updates */
export function upsertEnv(updates, path = ENV_PATH) {
  const lines = existsSync(path) ? readFileSync(path, 'utf8').split(/\r?\n/) : []
  const remaining = { ...updates }
  const out = []
  const seen = new Set()

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#') || !line.includes('=')) {
      out.push(line)
      continue
    }
    const key = line.slice(0, line.indexOf('=')).trim()
    if (key in remaining) {
      out.push(`${key}=${remaining[key]}`)
      seen.add(key)
      delete remaining[key]
    } else {
      out.push(line)
    }
  }

  for (const [key, value] of Object.entries(remaining)) {
    if (!seen.has(key)) out.push(`${key}=${value}`)
  }

  let text = out.join('\n')
  if (text && !text.endsWith('\n')) text += '\n'
  writeFileSync(path, text, 'utf8')
}
