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

// Auth
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

// Settings
export async function getSettings() {
  return request('/settings')
}

export async function updateSettings(data) {
  return request('/settings', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

// Stats
export async function getTodayStats() {
  return request('/stats/today')
}

export async function getWeekStats() {
  return request('/stats/week')
}

export async function getMonthStats() {
  return request('/stats/month')
}

export async function addIntake(amount_ml) {
  return request('/stats/intake', {
    method: 'POST',
    body: JSON.stringify({ amount_ml }),
  })
}
