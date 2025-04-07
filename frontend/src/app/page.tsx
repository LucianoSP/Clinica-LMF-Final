'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);

  // Garantir que o código só execute no cliente
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Redirecionar apenas quando estiver montado
  useEffect(() => {
    if (isMounted) {
      // Use um timeout para evitar erros de redirecionamento imediato
      const redirectTimer = setTimeout(() => {
        router.replace('/dashboard');
      }, 100);
      
      return () => clearTimeout(redirectTimer);
    }
  }, [router, isMounted]);

  // Renderizar um indicador de carregamento ou nada
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-pulse text-gray-400">Carregando...</div>
    </div>
  );
}