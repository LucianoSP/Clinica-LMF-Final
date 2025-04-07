'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function NotFound() {
  const router = useRouter();
  const [countdown, setCountdown] = useState(5);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          router.push('/dashboard');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [router]);
  
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
      <h1 className="text-4xl font-bold mb-4">Página não encontrada</h1>
      <p className="text-xl mb-6">Desculpe, a página que você está procurando não existe.</p>
      <p className="mb-8">
        Você será redirecionado para a página inicial em {countdown} segundos ou pode
        clicar no botão abaixo.
      </p>
      <Link href="/dashboard">
        <button className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors">
          Ir para a página inicial
        </button>
      </Link>
    </div>
  );
} 