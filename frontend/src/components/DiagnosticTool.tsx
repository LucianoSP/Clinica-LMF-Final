'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export function DiagnosticTool() {
  const [isVisible, setIsVisible] = useState(false)
  const [diagnostics, setDiagnostics] = useState<{
    online: boolean;
    supabaseConnected: boolean;
    errors: string[];
    lastChecked: string;
  }>({
    online: true,
    supabaseConnected: false,
    errors: [],
    lastChecked: new Date().toISOString()
  })

  useEffect(() => {
    // Verifica o estado inicial
    checkStatus();
    
    // Configura verificação periódica
    const interval = setInterval(checkStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    const errors: string[] = [];
    let supabaseConnected = false;
    
    // Verifica conexão com a internet
    const online = navigator.onLine;
    
    // Verifica conexão com o Supabase
    try {
      const { data, error } = await supabase.auth.getSession();
      if (error) {
        errors.push(`Erro Supabase: ${error.message}`);
      } else {
        supabaseConnected = true;
      }
    } catch (error) {
      errors.push(`Exceção ao conectar com Supabase: ${error instanceof Error ? error.message : String(error)}`);
    }
    
    setDiagnostics({
      online,
      supabaseConnected,
      errors,
      lastChecked: new Date().toISOString()
    });
  };
  
  // Tecla de atalho para mostrar/esconder (Ctrl+Shift+D)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        setIsVisible(prev => !prev);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  if (!isVisible) return null;
  
  return (
    <div className="fixed bottom-4 left-4 z-50 p-4 bg-white rounded-lg shadow-lg border border-gray-200 max-w-md">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-bold">Diagnóstico do Sistema</h3>
        <button 
          onClick={() => setIsVisible(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          X
        </button>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex items-center">
          <span className="mr-2">Status da Conexão:</span>
          <span className={`px-2 py-1 rounded ${diagnostics.online ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {diagnostics.online ? 'Online' : 'Offline'}
          </span>
        </div>
        
        <div className="flex items-center">
          <span className="mr-2">Conexão Supabase:</span>
          <span className={`px-2 py-1 rounded ${diagnostics.supabaseConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {diagnostics.supabaseConnected ? 'Conectado' : 'Desconectado'}
          </span>
        </div>
        
        {diagnostics.errors.length > 0 && (
          <div>
            <span className="font-semibold">Erros:</span>
            <ul className="list-disc pl-5 mt-1 text-red-600">
              {diagnostics.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="text-xs text-gray-500">
          Última verificação: {new Date(diagnostics.lastChecked).toLocaleTimeString()}
        </div>
        
        <button 
          onClick={checkStatus}
          className="w-full mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Verificar Novamente
        </button>
      </div>
    </div>
  )
} 