import { useState } from 'react'
import { AppProvider, useApp } from './hooks/useApp'
import TodayScreen from './screens/TodayScreen'
import StatsScreen from './screens/StatsScreen'
import SettingsScreen from './screens/SettingsScreen'
import './styles.css'

const NAV = [
  {
    key: 'today',
    label: 'Сегодня',
    icon: (active) => (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" fill={active ? 'currentColor' : 'none'} fillOpacity="0.15" />
        <path d="M12 7 C10 10, 8 12, 12 16 C16 12, 14 10, 12 7Z" fill="currentColor" />
      </svg>
    )
  },
  {
    key: 'stats',
    label: 'Статистика',
    icon: (active) => (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <rect x="4" y="14" width="3" height="6" rx="1.5" fill="currentColor" fillOpacity={active ? 1 : 0.5} />
        <rect x="10.5" y="9" width="3" height="11" rx="1.5" fill="currentColor" fillOpacity={active ? 1 : 0.7} />
        <rect x="17" y="4" width="3" height="16" rx="1.5" fill="currentColor" />
      </svg>
    )
  },
  {
    key: 'settings',
    label: 'Настройки',
    icon: (active) => (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.5" />
        <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
          stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    )
  },
]

function Inner() {
  const { loading, error } = useApp()
  const [tab, setTab] = useState('today')

  if (loading) {
    return (
      <div className="splash">
        <div className="splash-icon">💧</div>
        <div className="loader" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="splash">
        <p className="error-msg">Ошибка: {error}</p>
      </div>
    )
  }

  return (
    <div className="app-shell">
      <div className="screen-container">
        {tab === 'today' && <TodayScreen />}
        {tab === 'stats' && <StatsScreen />}
        {tab === 'settings' && <SettingsScreen />}
      </div>

      <nav className="bottom-nav">
        {NAV.map(n => (
          <button
            key={n.key}
            className={`nav-btn ${tab === n.key ? 'active' : ''}`}
            onClick={() => setTab(n.key)}
          >
            <span className="nav-icon">{n.icon(tab === n.key)}</span>
            <span className="nav-label">{n.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}

export default function App() {
  return (
    <AppProvider>
      <Inner />
    </AppProvider>
  )
}
