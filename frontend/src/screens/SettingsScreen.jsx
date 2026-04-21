import { useState, useEffect, useRef } from 'react'
import { useApp } from '../hooks/useApp'
import { updateSettings } from '../utils/api'

const TZ_OPTIONS = [
  'Europe/Tallinn', 'Europe/Moscow', 'Europe/Kiev', 'Europe/Minsk',
  'Europe/Riga', 'Europe/Vilnius', 'Europe/Helsinki', 'Europe/Warsaw',
  'Europe/Berlin', 'Europe/London', 'America/New_York', 'America/Los_Angeles',
  'Asia/Almaty', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Yerevan',
]

function RangeSlider({ label, value, min, max, step = 1, unit, onChange, marks }) {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <div className="slider-field">
      <div className="slider-header">
        <span className="slider-label">{label}</span>
        <span className="slider-value">{value}{unit}</span>
      </div>
      <div className="slider-track-wrap">
        <div className="slider-fill" style={{ width: `${pct}%` }} />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={e => onChange(Number(e.target.value))}
          className="slider-input"
        />
      </div>
      {marks && (
        <div className="slider-marks">
          {marks.map(m => <span key={m}>{m}{unit}</span>)}
        </div>
      )}
    </div>
  )
}

export default function SettingsScreen() {
  const { settings, setSettings } = useApp()
  const [form, setForm] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const savedTimer = useRef(null)

  useEffect(() => {
    if (settings) setForm({ ...settings })
  }, [settings])

  function update(key, val) {
    setForm(prev => ({ ...prev, [key]: val }))
  }

  async function handleSave() {
    if (saving) return
    setSaving(true)
    try {
      const updated = await updateSettings(form)
      setSettings(updated)
      setSaved(true)
      clearTimeout(savedTimer.current)
      savedTimer.current = setTimeout(() => setSaved(false), 2500)
    } catch (e) {
      alert(`Ошибка сохранения: ${e.message}`)
    } finally {
      setSaving(false)
    }
  }

  if (!form) return <div className="screen-loading"><div className="loader" /></div>

  const intervalHours = Math.floor(form.interval / 60)
  const intervalMins = form.interval % 60
  const intervalLabel = intervalHours > 0
    ? `${intervalHours}ч ${intervalMins > 0 ? intervalMins + 'м' : ''}`.trim()
    : `${form.interval}м`

  return (
    <div className="screen settings-screen">
      <div className="settings-header">
        <h1 className="today-title">Настройки</h1>
      </div>

      <div className="settings-sections">
        {/* Goals */}
        <div className="settings-group">
          <p className="group-title">Цели</p>
          <RangeSlider
            label="Дневная цель"
            value={form.daily_goal}
            min={500}
            max={4000}
            step={50}
            unit=" мл"
            onChange={v => update('daily_goal', v)}
            marks={[500, 1500, 2500, 4000]}
          />
          <div className="goal-presets">
            {[1500, 2000, 2500, 3000].map(g => (
              <button
                key={g}
                className={`preset-btn ${form.daily_goal === g ? 'active' : ''}`}
                onClick={() => update('daily_goal', g)}
              >
                {g / 1000}л
              </button>
            ))}
          </div>
        </div>

        {/* Reminders */}
        <div className="settings-group">
          <p className="group-title">Напоминания</p>
          <RangeSlider
            label="Интервал"
            value={form.interval}
            min={15}
            max={240}
            step={15}
            unit="м"
            onChange={v => update('interval', v)}
          />
          <div className="interval-display">
            каждые <strong>{intervalLabel}</strong>
          </div>
        </div>

        {/* Active hours */}
        <div className="settings-group">
          <p className="group-title">Активные часы</p>
          <div className="hours-row">
            <div className="hour-select">
              <label className="hour-select-label">С</label>
              <select
                className="select-field"
                value={form.start_hour}
                onChange={e => update('start_hour', Number(e.target.value))}
              >
                {Array.from({ length: 24 }, (_, i) => (
                  <option key={i} value={i}>{String(i).padStart(2, '0')}:00</option>
                ))}
              </select>
            </div>
            <div className="hours-arrow">→</div>
            <div className="hour-select">
              <label className="hour-select-label">До</label>
              <select
                className="select-field"
                value={form.end_hour}
                onChange={e => update('end_hour', Number(e.target.value))}
              >
                {Array.from({ length: 24 }, (_, i) => (
                  <option key={i} value={i}>{String(i).padStart(2, '0')}:00</option>
                ))}
              </select>
            </div>
          </div>
          <p className="hours-hint">
            напоминания с {String(form.start_hour).padStart(2,'0')}:00 до {String(form.end_hour).padStart(2,'0')}:00
          </p>
        </div>

        {/* Timezone */}
        <div className="settings-group">
          <p className="group-title">Часовой пояс</p>
          <select
            className="select-field full"
            value={form.timezone}
            onChange={e => update('timezone', e.target.value)}
          >
            {TZ_OPTIONS.map(tz => (
              <option key={tz} value={tz}>{tz.replace('_', ' ')}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Save button */}
      <div className="save-wrap">
        <button
          className={`save-btn ${saved ? 'saved' : ''}`}
          onClick={handleSave}
          disabled={saving}
        >
          {saved ? '✓ Сохранено' : saving ? 'Сохранение…' : 'Сохранить'}
        </button>
      </div>
    </div>
  )
}
