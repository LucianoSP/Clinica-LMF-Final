'use client'

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Home, Users, FileText, Calendar, ClipboardList, Database, HardDrive, BarChart, LogOut } from "lucide-react"
import { usePathname } from "next/navigation"
import { useAuth } from '@/hooks/useAuth'
import Link from 'next/link'
import React, { useEffect, useState } from 'react'
import type { Usuario } from '@/types/supabase'
import { useRouter } from 'next/navigation'

// Primeiro, definir os tipos permitidos para variant
type ButtonVariant = "default" | "link" | "secondary" | "destructive" | "outline" | "ghost";

// Atualizar a interface do item para usar o tipo correto
interface SidebarItem {
  title: string;
  href?: string;
  icon: React.ComponentType<{ className?: string }>;
  variant?: ButtonVariant;
  className?: string;
}

const sidebarItems: SidebarItem[] = [
  {
    title: "Gestão de Faturamento",
    icon: Database,
    variant: "ghost",
    className: "font-semibold px-4 py-8 justify-start w-full border-b border-slate-200/20 text-lg",
  },
  {
    title: "Home",
    icon: Home,
    href: "/dashboard",
  },
  {
    title: "Cadastros",
    icon: FileText,
    href: "/cadastros",
  },
    {
    title: "Pacientes",
    icon: ClipboardList,
    href: "/fichas-presenca",
  },
  {
    title: "Fichas",
    icon: Database,
    href: "/fichas",
  },
  {
    title: "Execuções",
    icon: Database,
    href: "/execucoes",
  },
  {
    title: "Agendamentos",
    icon: Calendar,
    href: "/agendamento",
  },
  {
    title: "Vinculações",
    icon: HardDrive,
    href: "/vinculacoes",
  },
  {
    title: "Auditoria",
    icon: BarChart,
    href: "/auditoria",
  },
  {
    title: "Unimed",
    icon: Users,
    href: "/unimed",
  },
  {
    title: "Armazenamento",
    icon: HardDrive,
    href: "/storage",
  },
  {
    title: "Documentação",
    icon: HardDrive,
    href: "/documentacao",
  },
 
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, signOut } = useAuth()
  const [isClient, setIsClient] = useState(false)
  const [userInfo, setUserInfo] = useState<Usuario | null>(null)
  const router = useRouter()

  // Garantir que a renderização do user só aconteça no cliente
  useEffect(() => {
    setIsClient(true)
    // Verificar se o usuário está realmente disponível
    if (user) {
      setUserInfo(user)
    }
  }, [user])

  // Efeito para verificar se estamos realmente autenticados
  useEffect(() => {
    if (isClient && !user) {
      // Verificar localmente se há tokens válidos
      const hasToken = 
        localStorage.getItem('supabase.auth.token') || 
        localStorage.getItem('sb-wpufnegczzdbuztgpxab-auth-token');
      
      // Se não encontrar tokens, redirecionar para login
      if (!hasToken) {
        window.location.href = '/login';
      }
    }
  }, [isClient, user])

  const handleLogout = async () => {
    try {
      // Desativar o estado do cliente antes do logout para evitar problemas de UI
      setIsClient(false);
      setUserInfo(null);
      
      // Executar o logout usando o hook global
      await signOut();
      
      // Navegar para a página de login usando o router
      router.push('/login');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      // Mesmo em caso de erro, tentar navegar para login
      router.push('/login');
    }
  }

  // Não renderizar nada até que seja confirmado que estamos no cliente
  if (!isClient) {
    return null;
  }

  return (
    <aside className="fixed inset-y-0 left-0 z-30 h-screen w-64 border-r bg-gradient-to-b from-slate-900 to-slate-800">
      <div className="flex h-full flex-col">
        <div className="flex-1">
          <div className="space-y-1 py-2">
            {sidebarItems.map((item) => (
              <Button
                key={item.title}
                variant={item.variant || "ghost"}
                className={cn(
                  "relative w-full justify-start gap-4 px-5 py-3.5 text-base font-normal text-slate-300 hover:text-slate-100 hover:bg-slate-800/50",
                  item.className,
                  pathname === item.href &&
                  "bg-slate-800/50 font-medium text-teal-400 before:absolute before:left-0 before:top-0 before:h-full before:w-1 before:bg-teal-500",
                )}
                asChild={item.href ? true : false}
              >
                {item.href ? (
                  <Link
                    href={item.href}
                    className="flex items-center"
                  >
                    {item.icon && React.createElement(item.icon, {
                      className: cn("h-5 w-5 mr-3", pathname === item.href ? "text-teal-400" : "text-slate-400")
                    })}
                    <span>{item.title}</span>
                  </Link>
                ) : (
                  <div className="flex items-center">
                    {item.icon && React.createElement(item.icon, {
                      className: "h-5 w-5 mr-3 text-teal-400"
                    })}
                    <span>{item.title}</span>
                  </div>
                )}
              </Button>
            ))}
          </div>
        </div>

        {isClient && userInfo && (
          <div className="border-t border-slate-200/10 p-5">
            <div className="space-y-2">
              <p className="text-base text-slate-300">{userInfo.nome}</p>
              <p className="text-sm text-slate-400">{userInfo.email}</p>
              <Button
                variant="ghost"
                className="w-full justify-start gap-4 mt-3 py-3.5 text-base text-slate-300 hover:text-slate-100 hover:bg-slate-800/50"
                onClick={handleLogout}
              >
                <LogOut className="h-5 w-5 mr-3 text-slate-400" />
                <span>Sair</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}