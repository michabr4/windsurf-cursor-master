#!/usr/bin/env node
/**
 * One-time Asana OAuth setup — saves tokens to .env (never logs raw values).
 */
import { createServer } from 'node:http'
import { randomBytes } from 'node:crypto'
import { spawn } from 'node:child_process'
import { URL, URLSearchParams } from 'node:url'
import { loadEnv, upsertEnv } from './asana-env.js'

const TOKEN_URL = 'https://app.asana.com/-/oauth_token'
const AUTHORIZE_URL = 'https://app.asana.com/-/oauth_authorize'

const env = loadEnv()
const clientId = (env.ASANA_CLIENT_ID || '').trim()
const clientSecret = (env.ASANA_CLIENT_SECRET || '').trim()
const port = (env.ASANA_REVIEW_PORT || '8845').trim() || '8845'
const redirectUri =
  (env.ASANA_OAUTH_REDIRECT_URI || '').trim() ||
  `http://127.0.0.1:${port}/oauth/callback`

if (!clientId || !clientSecret) {
  console.error('Missing ASANA_CLIENT_ID or ASANA_CLIENT_SECRET in .env')
  console.error('Add them from the Asana Developer Console, then run: npm run setup-oauth')
  process.exit(1)
}

const redirect = new URL(redirectUri)
const callbackPath = redirect.pathname || '/oauth/callback'
const state = randomBytes(32).toString('hex')

/** @param {Record<string, string>} form */
async function exchangeToken(form) {
  const body = new URLSearchParams(form)
  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
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
  return payload
}

function openBrowser(url) {
  const platform = process.platform
  if (platform === 'darwin') spawn('open', [url], { stdio: 'ignore', detached: true })
  else if (platform === 'win32') spawn('cmd', ['/c', 'start', '', url], { stdio: 'ignore', detached: true })
  else spawn('xdg-open', [url], { stdio: 'ignore', detached: true })
}

const authParams = new URLSearchParams({
  client_id: clientId,
  redirect_uri: redirectUri,
  response_type: 'code',
  state,
})
const authorizeUrl = `${AUTHORIZE_URL}?${authParams}`

const server = createServer(async (req, res) => {
  try {
    const reqUrl = new URL(req.url || '/', `http://127.0.0.1:${port}`)
    if (reqUrl.pathname !== callbackPath) {
      res.writeHead(404, { 'Content-Type': 'text/plain' })
      res.end('Not found')
      return
    }

    const code = reqUrl.searchParams.get('code')
    const returnedState = reqUrl.searchParams.get('state')
    const err = reqUrl.searchParams.get('error')

    if (err) {
      res.writeHead(400, { 'Content-Type': 'text/html' })
      res.end(`<h1>Authorization failed</h1><p>${err}</p>`)
      server.close()
      process.exit(1)
      return
    }

    if (!code || returnedState !== state) {
      res.writeHead(400, { 'Content-Type': 'text/html' })
      res.end('<h1>Invalid callback</h1><p>Missing code or state mismatch.</p>')
      server.close()
      process.exit(1)
      return
    }

    await exchangeToken({
      grant_type: 'authorization_code',
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
      code,
    })

    res.writeHead(200, { 'Content-Type': 'text/html' })
    res.end(
      '<h1>Asana connected</h1><p>You can close this tab and return to the terminal.</p>',
    )
    console.log('✅ Tokens saved to .env')
    console.log('Next: npm run fetch')
    server.close()
    process.exit(0)
  } catch (e) {
    console.error(e instanceof Error ? e.message : e)
    res.writeHead(500, { 'Content-Type': 'text/plain' })
    res.end('Token exchange failed')
    server.close()
    process.exit(1)
  }
})

server.listen(Number(port), '127.0.0.1', () => {
  console.log(`Listening on http://127.0.0.1:${port}${callbackPath}`)
  console.log('Opening browser for Asana authorization…')
  openBrowser(authorizeUrl)
})

server.on('error', err => {
  console.error(err.message)
  process.exit(1)
})

setTimeout(() => {
  console.error('OAuth setup timed out after 10 minutes.')
  server.close()
  process.exit(1)
}, 10 * 60 * 1000)
