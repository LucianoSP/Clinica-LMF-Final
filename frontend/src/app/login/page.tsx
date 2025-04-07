'use client'

import { useAuth } from "@/hooks/useAuth"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { BrandingSection } from "@/components/login/BrandingSection"
import { LoginCard } from "@/components/login/LoginCard"
import "@/styles/animations.css"
import { toast } from "sonner"

export default function LoginPage() {
  const { user, loading, signIn } = useAuth()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  // Simplificando o redirecionamento - apenas um único useEffect
  useEffect(() => {
    // Se o usuário estiver autenticado, redireciona para o dashboard
    if (!loading && user) {
      // Registrar no console para debug
      console.log("Login: usuário autenticado, navegando para dashboard");
      // Usar router para navegação para garantir uso do Next Router
      router.replace('/dashboard');
    }
  }, [user, loading, router]);

  const handleSubmit = async (email: string, password: string) => {
    // Evitar múltiplos cliques
    if (isLoading) return;
    
    setIsLoading(true);
    try {
      // Realizar login - o redirecionamento ocorrerá via useEffect quando user não for null
      await signIn(email, password);
      toast.success('Login realizado com sucesso!');
      // Não redirecionar aqui - o useEffect cuida disso
    } catch (error: any) {
      // Mensagem de erro amigável baseada no tipo de erro
      let errorMessage = 'Erro ao fazer login. Verifique suas credenciais e tente novamente.';
      
      if (error?.message?.includes('offline') || error?.message?.includes('network')) {
        errorMessage = 'Sem conexão com a internet. Verifique sua conexão e tente novamente.';
      } else if (error?.message?.includes('Invalid login credentials')) {
        errorMessage = 'Email ou senha incorretos. Tente novamente.';
      }
      
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Mostrar loading enquanto verifica a autenticação inicial
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 via-gray-100 to-white">
        <div className="animate-spin rounded-full h-24 w-24 border-t-4 border-blue-400"></div>
      </div>
    );
  }

  // Se o usuário já está autenticado, não mostrar a tela de login
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 via-gray-100 to-white">
        <div className="animate-spin rounded-full h-24 w-24 border-t-4 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full relative bg-gradient-to-br from-blue-500 via-gray-100 to-white flex items-center justify-center p-4 overflow-hidden">
      {/* Blobs animados no fundo */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-80 h-80 bg-gray-200 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      <div className="container flex justify-center items-center mx-auto z-10">
        <div className="grid lg:grid-cols-2 gap-8 w-full max-w-5xl">
          <BrandingSection />
          <div className="w-full max-w-md mx-auto animate-fadeInRight">
            <LoginCard onSubmit={handleSubmit} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </div>
  );
} 