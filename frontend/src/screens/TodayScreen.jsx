import { useState, useEffect, useRef } from 'react'
import { getTodayStats, addIntake } from '../utils/api'
import { useApp } from '../hooks/useApp'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
dayjs.locale('ru')

const QUICK_ADD = [150, 200, 250, 300, 500]

function WaveProgress({ percent }) {
  const clampedPercent = Math.min(100, Math.max(0, percent))
  const offset = 100 - clampedPercent
  const color1 = clampedPercent >= 100 ? '#34d399' : '#38bdf8'
  const color2 = clampedPercent >= 100 ? '#10b981' : '#0ea5e9'

  return (
    <div className="wave-wrapper" style={{ '--pct': `${offset}%`, '--c1': color1, '--c2': color2 }}>
      <svg viewBox="0 0 200 200" className="wave-svg">
        <defs>
          <clipPath id="circle-clip">
            <circle cx="100" cy="100" r="90" />
          </clipPath>
          <linearGradient id="water-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color1} stopOpacity="0.9" />
            <stop offset="100%" stopColor={color2} stopOpacity="0.7" />
          </linearGradient>
        </defs>
        <circle cx="100" cy="100" r="90" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.08)" strokeWidth="1" />
        <g clipPath="url(#circle-clip)">
          <rect x="-10" y="0" width="220" height="200" fill="url(#water-grad)" style={{
            transform: `translateY(${offset}%)`,
            transition: 'transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
          }} />
          <path
            d="M-10,0 Q20,-12 50,0 Q80,12 110,0 Q140,-12 170,0 Q200,12 220,0 L220,20 L-10,20 Z"
            fill={color1}
            opacity="0.5"
            style={{
              transform: `translateY(${offset}%)`,
              transition: 'transform 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
              animation: 'wave 3s ease-in-out infinite',
            }}
          />
        </g>
        <circle cx="100" cy="100" r="90" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="2" />
      </svg>
      <div className="wave-label">
        <span className="wave-pct">{clampedPercent.toFixed(0)}%</span>
      </div>
    </div>
  )
}

function EntryRow({ entry }) {
  const time = dayjs(entry.recorded_at).format('HH:mm')
  return (
    <div className="entry-row">
      <div className="entry-dot" />
      <span className="entry-time">{time}</span>
      <span className="entry-amount">+{entry.amount_ml} мл</span>
    </div>
  )
}

export default function TodayScreen() {
  const { settings } = useApp()
  const [stats, setStats] = useState(null)
  const [adding, setAdding] = useState(false)
  const [toast, setToast] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const toastTimer = useRef(null)

  useEffect(() => {
    getTodayStats()
      .then(setStats)
      .catch(e => setLoadError(e.message))
  }, [])

  async function handleQuickAdd(ml) {
    if (adding) return
    setAdding(true)
    try {
      const entry = await addIntake(ml)
      setStats(prev => ({
        ...prev,
        consumed_ml: prev.consumed_ml + ml,
        entries: [entry, ...prev.entries],
      }))
      showToast(`+${ml} мл`)
    } catch (e) {
      showToast(`Ошибка: ${e.message}`)
    } finally {
      setAdding(false)
    }
  }

  function showToast(msg) {
    setToast(msg)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToast(null), 2000)
  }

  if (loadError) return <div className="screen-loading"><p className="error-msg">Ошибка: {loadError}</p></div>
  if (!stats) return <div className="screen-loading"><div className="loader" /></div>

  const { consumed_ml, goal_ml, entries } = stats
  const percent = (consumed_ml / goal_ml) * 100
  const remaining = Math.max(0, goal_ml - consumed_ml)

  return (
    <div className="screen today-screen">
      {toast && <div className="toast">{toast}</div>}

      <div className="today-header">
        <h1 className="today-title">Сегодня</h1>
        <p className="today-sub">{dayjs().format('D MMMM, dddd')}</p>
      </div>

      <div className="progress-section">
        <WaveProgress percent={percent} />
        <div className="progress-numbers">
          <div className="consumed">
            <span className="num">{consumed_ml}</span>
            <span className="unit">мл</span>
          </div>
          <div className="divider-line" />
          <div className="goal">
            <span className="num">{goal_ml}</span>
            <span className="unit">цель</span>
          </div>
        </div>
        {remaining > 0 && (
          <p className="remaining-hint">ещё {remaining} мл до цели</p>
        )}
        {remaining === 0 && (
          <p className="remaining-hint achieved">🎉 цель достигнута!</p>
        )}
      </div>

      <div className="quick-section">
        <p className="section-label">Добавить</p>
        <div className="quick-buttons">
          {QUICK_ADD.map(ml => (
            <button
              key={ml}
              className="quick-btn"
              onClick={() => handleQuickAdd(ml)}
              disabled={adding}
            >
              <span className="quick-drop">💧</span>
              <span className="quick-ml">{ml}</span>
              <span className="quick-unit">мл</span>
            </button>
          ))}
        </div>
      </div>

      {entries.length > 0 && (
        <div className="entries-section">
          <p className="section-label">Записи</p>
          <div className="entries-list">
            {entries.map(e => <EntryRow key={e.id} entry={e} />)}
          </div>
        </div>
      )}
    </div>
  )
}
