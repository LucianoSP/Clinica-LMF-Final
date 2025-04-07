'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log do erro para análise
    console.error('Erro na aplicação:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Algo deu errado!</h2>
        <p className="text-gray-700 mb-6">
          Ocorreu um erro inesperado. Nossa equipe foi notificada e estamos trabalhando para resolver o problema.
        </p>
        <div className="flex flex-col space-y-3">
          <Button 
            onClick={() => reset()}
            className="w-full"
          >
            Tentar novamente
          </Button>
          <Button 
            onClick={() => window.location.href = '/dashboard'}
            variant="outline"
            className="w-full"
          >
            Voltar para o Dashboard
          </Button>
        </div>
      </div>
    </div>
  )
} 