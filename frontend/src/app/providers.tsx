'use client';

import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/hooks/useAuth';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        retry: 1,
        refetchOnWindowFocus: false,
        staleTime: 5 * 60 * 1000, // 5 minutos
      },
      mutations: {
        // Configurações para mutações
      }
    }
  }));
  const [isMounted, setIsMounted] = useState(false);

  // Evita problemas de hidratação garantindo que o componente só renderize no cliente
  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    // Retornar uma div vazia como placeholder para evitar erros de hidratação
    return <div className="contents">{children}</div>;
  }

  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </AuthProvider>
  );
}