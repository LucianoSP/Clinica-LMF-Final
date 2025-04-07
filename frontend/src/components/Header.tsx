"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "./ui/button";
import { useAuth } from "@/hooks/useAuth";

export function Header() {
  const [userName, setUserName] = useState<string>("");
  const [isMounted, setIsMounted] = useState(false);
  const router = useRouter();
  const { signOut } = useAuth();

  useEffect(() => {
    setIsMounted(true);
    const getUser = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (user?.user_metadata?.name) {
          setUserName(user.user_metadata.name);
        } else if (user?.email) {
          setUserName(user.email);
        }
      } catch (error) {
        console.error('Erro ao obter usuário:', error);
      }
    };

    getUser();
  }, []);

  const handleLogout = async () => {
    try {
      await signOut();
      // Após logout bem-sucedido, navegar para a página de login
      router.push('/login');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      // Em caso de erro, tentar redirecionar mesmo assim
      router.push('/login');
    }
  };

  if (!isMounted) {
    return null;
  }

  return (
    <header className="h-16 border-b bg-white">
      <div className="h-full flex items-center justify-between px-6">
        <div className="text-lg font-semibold text-slate-900">
          Sistema Médico
        </div>
        
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-600">
            {userName}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-slate-600 hover:text-slate-900"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
} 