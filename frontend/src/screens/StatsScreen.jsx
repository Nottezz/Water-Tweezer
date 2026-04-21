import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ReferenceLine,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { getWeekStats, getMonthStats } from '../utils/api'
import { useApp } from '../hooks/useApp'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
dayjs.locale('ru')

const TABS = [
  { key: 'week', label: 'Неделя' },
  { key: 'month', label: 'Месяц' },
]

function StatCard({ label, value, unit, accent }) {
  return (
    <div className="stat-card" style={{ '--accent': accent }}>
      <span className="stat-card-value">{value}<span className="stat-card-unit">{unit}</span></span>
      <span className="stat-card-label">{label}</span>
    </div>
  )
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="chart-tooltip">
      <div className="tooltip-date">{dayjs(d.date).format('D MMM')}</div>
      <div className="tooltip-val">{d.consumed_ml} мл</div>
      <div className="tooltip-pct">{Math.round(d.consumed_ml / d.goal_ml * 100)}% от цели</div>
    </div>
  )
}

function calcStreak(data) {
  let streak = 0
  const sorted = [...data].sort((a, b) => b.date.localeCompare(a.date))
  for (const d of sorted) {
    if (d.consumed_ml >= d.goal_ml) streak++
    else break
  }
  return streak
}

export default function StatsScreen() {
  const { settings } = useApp()
  const [tab, setTab] = useState('week')
  const [data, setData] = useState([])
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    setData([])
    setLoadError(null)
    const fetch = tab === 'week' ? getWeekStats : getMonthStats
    fetch()
      .then(setData)
      .catch(e => setLoadError(e.message))
  }, [tab])

  if (loadError) return <div className="screen-loading"><p className="error-msg">Ошибка: {loadError}</p></div>
  if (!data.length) return <div className="screen-loading"><div className="loader" /></div>

  const goal = settings?.daily_goal ?? 2000
  const avg = Math.round(data.reduce((s, d) => s + d.consumed_ml, 0) / data.length)
  const best = Math.max(...data.map(d => d.consumed_ml))
  const daysHit = data.filter(d => d.consumed_ml >= d.goal_ml).length
  const streak = calcStreak(data)

  const chartData = data.map(d => ({
    ...d,
    label: tab === 'week'
      ? dayjs(d.date).format('dd')
      : dayjs(d.date).format('D'),
    hit: d.consumed_ml >= goal,
  }))

  return (
    <div className="screen stats-screen">
      <div className="stats-header">
        <h1 className="today-title">Статистика</h1>

        {/* Tab switcher */}
        <div className="tab-switcher">
          {TABS.map(t => (
            <button
              key={t.key}
              className={`tab-btn ${tab === t.key ? 'active' : ''}`}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary cards */}
      <div className="stat-cards">
        <StatCard label="Среднее" value={avg} unit=" мл" accent="#38bdf8" />
        <StatCard label="Рекорд" value={best} unit=" мл" accent="#a78bfa" />
        <StatCard label="Выполнено" value={daysHit} unit={` / ${data.length}`} accent="#34d399" />
        <StatCard label="Стрик" value={streak} unit=" дн" accent="#fb923c" />
      </div>

      {/* Bar chart */}
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} barCategoryGap="30%" margin={{ top: 10, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="label"
              tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 11, fontFamily: 'DM Sans' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: 'rgba(255,255,255,0.25)', fontSize: 10, fontFamily: 'DM Sans' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={v => `${v / 1000}л`}
              domain={[0, Math.max(goal * 1.3, best * 1.1)]}
            />
            <ReferenceLine
              y={goal}
              stroke="#38bdf8"
              strokeDasharray="4 4"
              strokeOpacity={0.5}
              label={{ value: 'Цель', fill: '#38bdf8', fontSize: 10, dx: 4 }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
            <Bar dataKey="consumed_ml" radius={[5, 5, 0, 0]} maxBarSize={32}>
              {chartData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.hit
                    ? 'url(#bar-hit)'
                    : 'rgba(56, 189, 248, 0.25)'}
                />
              ))}
            </Bar>
            <defs>
              <linearGradient id="bar-hit" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.6" />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
        <p className="chart-legend">
          <span className="legend-dot hit" /> выполнено &nbsp;
          <span className="legend-dot miss" /> не достигнуто
        </p>
      </div>

      {/* Daily breakdown */}
      <div className="breakdown-section">
        <p className="section-label">По дням</p>
        <div className="breakdown-list">
          {[...chartData].reverse().slice(0, 7).map((d, i) => {
            const pct = Math.min(100, Math.round(d.consumed_ml / goal * 100))
            return (
              <div key={i} className="breakdown-row">
                <span className="breakdown-date">{dayjs(d.date).format('D MMM')}</span>
                <div className="breakdown-bar-wrap">
                  <div
                    className={`breakdown-bar ${d.hit ? 'hit' : ''}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className={`breakdown-ml ${d.hit ? 'hit' : ''}`}>{d.consumed_ml}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
