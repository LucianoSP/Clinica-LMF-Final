'use client'

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Sidebar } from "@/components/Sidebar";
import { LoadingScreen } from "@/components/LoadingScreen";
import { Session } from "@supabase/supabase-js";
import { OfflineIndicator } from "@/components/OfflineIndicator";
import { DiagnosticTool } from "@/components/DiagnosticTool";
import { useAuth } from "@/hooks/useAuth";

interface AuthLayoutProps {
  children: React.ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  const { user, loading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);
  const router = useRouter();

  // Evita problemas de hidratação garantindo que o componente só renderize no cliente
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Verificar se o usuário está autenticado e redirecionar se necessário
  useEffect(() => {
    if (!isMounted || authLoading) return;
    
    // Se não há usuário, redireciona para a página de login
    if (!user) {
      console.log("[AuthLayout] Usuário não autenticado, redirecionando para login");
      router.replace('/login');
    } else {
      console.log("[AuthLayout] Usuário autenticado, permitindo acesso");
      setIsLoading(false);
    }
  }, [user, authLoading, isMounted, router]);

  // Não renderiza nada durante a montagem inicial para evitar problemas de hidratação
  if (!isMounted) {
    return null;
  }

  // Enquanto estiver verificando a autenticação
  if (isLoading || authLoading) {
    return <LoadingScreen />;
  }

  // Se o usuário não estiver autenticado, não deveria chegar aqui (mas por segurança)
  if (!user) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar />
      <main className="flex-1 ml-64">
        {children}
        <OfflineIndicator />
        <DiagnosticTool />
      </main>
    </div>
  );
} 