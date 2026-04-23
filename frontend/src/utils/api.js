// API client — uses JWT from Telegram initData verification
// Token is stored in memory (not localStorage per security best practices)

let authToken = null

export function setToken(token) {
  authToken = token
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    ...options.headers,
  }
  const res = await fetch(`/api${path}`, { ...options, headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export async function verifyTelegramAuth(initData) {
  const res = await fetch('/auth/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ init_data: initData }),
  })
  if (!res.ok) throw new Error('Auth failed')
  const { access_token } = await res.json()
  setToken(access_token)
  return access_token
}

// ─── Settings ─────────────────────────────────────────────────────────────────

// GET /api/settings/ → { telegram_id, daily_goal, interval, timezone }
export async function getSettings() {
  return request('/settings/')
}

// POST /api/settings/ → { telegram_id, daily_goal, interval, timezone }
export async function updateSettings(data) {
  return request('/settings/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// ─── Stats ────────────────────────────────────────────────────────────────────

// GET /api/stats/today → number (total ml consumed today)
// Normalised to { consumed_ml, goal_ml, entries } for TodayScreen
export async function getTodayStats(goalMl) {
  const consumed_ml = await request('/stats/today')
  return {
    consumed_ml,
    goal_ml: goalMl,
    entries: [],
  }
}

// GET /api/stats/week → [{ day, total }, ...]
// Normalised to [{ date, consumed_ml, goal_ml }, ...] for StatsScreen
export async function getWeekStats(goalMl) {
  const raw = await request('/stats/week')
  return raw.map(({ day, total }) => ({
    date: day,
    consumed_ml: total,
    goal_ml: goalMl,
  }))
}

// GET /api/stats/month → deprecated на бэкенде, пока не реализован
export async function getMonthStats(goalMl) {
  const raw = await request('/stats/month')
  return (raw ?? []).map(({ day, total }) => ({
    date: day,
    consumed_ml: total,
    goal_ml: goalMl,
  }))
}

// POST /api/stats/intake → WaterIntake record
export async function addIntake(amount_ml) {
  return request('/stats/intake', {
    method: 'POST',
    body: JSON.stringify({ amount_ml }),
  })
}
