import { LEGACY_SESSION_KEYS, SESSION_KEY } from '../constants.js';

export function readSessionState() {
  if (typeof window === 'undefined') return {};
  try {
    const keysToTry = [SESSION_KEY, ...LEGACY_SESSION_KEYS];
    for (const key of keysToTry) {
      const raw = window.localStorage.getItem(key);
      if (!raw) continue;
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) continue;
      return parsed;
    }
    return {};
  } catch {
    return {};
  }
}

export function writeSessionState(state) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(state));
}
