'use client'

import { useState, useEffect } from 'react';

interface LoadingScreenProps {
  message?: string;
}

export function LoadingScreen({ message = "Carregando..." }: LoadingScreenProps) {
  const [loadingTime, setLoadingTime] = useState(0);
  const [showRetryButton, setShowRetryButton] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setLoadingTime(prev => {
        const newTime = prev + 1;
        // Se demorar mais de 10 segundos, mostra o botão de retry
        if (newTime > 10) {
          setShowRetryButton(true);
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleRetry = () => {
    // Recarrega a página
    window.location.reload();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50">
      <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-lg text-gray-700 mb-2">{message}</p>
      
      {showRetryButton && (
        <div className="mt-4 text-center">
          <p className="text-amber-600 mb-2">
            Está demorando mais que o esperado. Pode haver um problema de conexão.
          </p>
          <button 
            onClick={handleRetry}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Tentar novamente
          </button>
        </div>
      )}
    </div>
  );
} 