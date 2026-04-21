import { createContext, useContext, useState, useEffect } from 'react'
import { verifyTelegramAuth, getSettings } from '../utils/api'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [user, setUser] = useState(null)
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function init() {
      try {
        const tg = window.Telegram?.WebApp
        if (tg) {
          tg.ready()
          tg.expand()
          await verifyTelegramAuth(tg.initData)
          setUser(tg.initDataUnsafe?.user || { first_name: 'User' })
        } else {
          setUser({ first_name: 'Dev' })
        }
        setSettings(await getSettings())
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [])

  return (
    <AppContext.Provider value={{ user, settings, setSettings, loading, error }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  return useContext(AppContext)
}
