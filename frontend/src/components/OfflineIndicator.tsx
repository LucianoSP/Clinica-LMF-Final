'use client'

import { useState, useEffect } from 'react'
import { AlertCircle, WifiOff } from 'lucide-react'

export function OfflineIndicator() {
  const [isOffline, setIsOffline] = useState(false)
  const [showBanner, setShowBanner] = useState(false)

  useEffect(() => {
    // Verifica o estado inicial
    setIsOffline(!navigator.onLine)
    
    // Configura os listeners
    const handleOnline = () => {
      setIsOffline(false)
      // Mostra o banner brevemente quando a conexão é restabelecida
      setShowBanner(true)
      setTimeout(() => setShowBanner(false), 3000)
    }
    
    const handleOffline = () => {
      setIsOffline(true)
      setShowBanner(true)
    }
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])
  
  if (!showBanner) return null
  
  return (
    <div className={`fixed bottom-4 right-4 z-50 p-3 rounded-lg shadow-lg flex items-center gap-2 transition-all duration-300 ${isOffline ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
      {isOffline ? (
        <>
          <WifiOff size={18} />
          <span>Você está offline. Algumas funcionalidades podem não estar disponíveis.</span>
        </>
      ) : (
        <>
          <AlertCircle size={18} />
          <span>Conexão restabelecida!</span>
        </>
      )}
    </div>
  )
} 