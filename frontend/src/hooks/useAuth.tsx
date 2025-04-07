'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { supabase } from '@/lib/supabase'
import type { Usuario } from '@/types/supabase'
import { useRouter } from 'next/navigation'
import { Session } from '@supabase/supabase-js'
import { toast } from 'sonner'

interface AuthContextType {
  user: Usuario | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  isOffline: boolean
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

interface AuthUser {
  id: string;
  email?: string;
}

// Fila de operações pendentes para executar quando online
const pendingOperations: Array<() => Promise<void>> = [];

// Função para tentar uma operação com retry e tratamento de erros melhorado
const retryOperation = async <T,>(
  operation: () => Promise<T>,
  maxRetries = 3,
  delay = 1000,
  operationName = 'Operação'
): Promise<T> => {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error: any) {
      lastError = error;
      
      // Verifica se é um erro de rede/conexão
      const isNetworkError = error.message?.includes('Failed to fetch') || 
                            error.message?.includes('Network Error') ||
                            error.message?.includes('Navegador offline');
      
      if (isNetworkError && typeof navigator !== 'undefined' && !navigator.onLine) {
        throw new Error('Dispositivo offline');
      }
      
      // Aguarda antes de tentar novamente
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // Aumenta o delay para a próxima tentativa (backoff exponencial)
      delay *= 1.5;
    }
  }
  
  throw lastError;
};

// Função para adicionar operação à fila quando offline
const queueOperationIfOffline = (operation: () => Promise<void>, operationName: string) => {
  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    console.log(`Dispositivo offline. Adicionando ${operationName} à fila para execução posterior.`);
    pendingOperations.push(operation);
    return true;
  }
  return false;
};

// Função para processar a fila de operações pendentes
const processPendingOperations = async () => {
  if (pendingOperations.length === 0) return;
  
  console.log(`Processando ${pendingOperations.length} operações pendentes...`);
  
  // Cria uma cópia da fila atual
  const operations = [...pendingOperations];
  // Limpa a fila original
  pendingOperations.length = 0;
  
  for (const operation of operations) {
    try {
      await operation();
    } catch (error) {
      console.error('Erro ao processar operação pendente:', error);
      // Se falhar, coloca de volta na fila
      pendingOperations.push(operation);
    }
  }
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Usuario | null>(null)
  const [loading, setLoading] = useState(true)
  const [isMounted, setIsMounted] = useState(false)
  const [isOffline, setIsOffline] = useState(false)
  const router = useRouter()

  // Evita problemas de hidratação
  useEffect(() => {
    setIsMounted(true);
    
    // Configura os listeners de online/offline
    if (typeof window !== 'undefined') {
      setIsOffline(!navigator.onLine);
      
      const handleOnline = () => {
        setIsOffline(false);
        processPendingOperations();
      };
      
      const handleOffline = () => {
        setIsOffline(true);
      };
      
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);
      
      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }
  }, []);

  // Função para atualizar o último acesso do usuário
  const updateLastAccess = async (userId: string): Promise<void> => {
    const updateOperation = async () => {
      try {
        // Se estiver offline, não tentar atualizar
        if (isOffline) {
          console.log('Dispositivo offline, pulando atualização de último acesso');
          return;
        }
        
        // Obter o token de autenticação atual
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;
        
        if (!token) {
          console.log('Sem token de autenticação, pulando atualização de último acesso');
          return;
        }
        
        // Primeiro, usar nossa rota de proxy para obter o ID do usuário
        const userResponse = await fetch(
          `/api/supabase?table=usuarios&auth_user_id=eq.${userId}&select=id`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          }
        );
        
        if (!userResponse.ok) {
          console.log(`Não foi possível obter o usuário: ${userResponse.statusText}`);
          return;
        }
        
        const users = await userResponse.json();
        if (!users || !Array.isArray(users) || users.length === 0) {
          console.log('Usuário não encontrado');
          return;
        }
        
        const primaryKeyId = users[0].id;
        
        // Depois, atualizar o último acesso usando a rota de proxy
        const updateResponse = await fetch(
          `/api/supabase?table=usuarios&id=eq.${primaryKeyId}`,
          {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
              'Prefer': 'return=representation'
            },
            body: JSON.stringify({ ultimo_acesso: new Date().toISOString() })
          }
        );
        
        if (!updateResponse.ok && updateResponse.status !== 204) {
          console.log(`Não foi possível atualizar o último acesso: ${updateResponse.statusText}`);
          return;
        }
        
        console.log('Último acesso atualizado com sucesso');
      } catch (error) {
        console.error('Erro ao atualizar último acesso:', error);
        // Não tentar novamente em caso de erro para evitar ciclos
      }
    };
    
    // Executar operação apenas se online
    if (!isOffline) {
      await updateOperation().catch(error => {
        console.error('Erro ao executar atualização de último acesso:', error);
      });
    }
  };

  const getOrCreateUser = async (authUser: AuthUser) => {
    try {
      // Tenta buscar o usuário existente com retry
      const { data: existingUser, error: fetchError } = await retryOperation(
        async () => {
          return await supabase
            .from('usuarios')
            .select('*')
            .eq('auth_user_id', authUser.id)
            .single()
        },
        3,
        1000,
        'Busca de usuário'
      );

      if (fetchError) {
        throw fetchError;
      }

      if (existingUser) {
        // Atualiza o último acesso em segundo plano
        updateLastAccess(authUser.id).catch(() => {
          // Silenciando erros de atualização de último acesso
        });
        
        return existingUser;
      }

      // Se não existir, cria um novo usuário
      try {
        const userData = {
          id: authUser.id,
          auth_user_id: authUser.id,
          email: authUser.email,
          nome: authUser.email?.split('@')[0] || 'Usuário',
          ultimo_acesso: new Date().toISOString(),
        };

        // Usamos o endpoint REST diretamente em vez de usar o builder para controle total
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/usuarios`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
              'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''}`,
              'Prefer': 'return=representation'
            },
            body: JSON.stringify([userData])
          }
        );

        if (!response.ok) {
          throw new Error(`Erro ao criar usuário: ${response.statusText}`);
        }

        const newUser = await response.json();
        return Array.isArray(newUser) ? newUser[0] : newUser;
      } catch (error) {
        throw error;
      }
    } catch (error) {
      // Notifica o usuário sobre o problema
      if (!isOffline) {
        toast.error('Erro ao conectar com o servidor. Algumas funcionalidades podem estar limitadas.');
      }
      
      // Retorna um usuário temporário para evitar erros na UI
      return {
        id: authUser.id,
        auth_user_id: authUser.id,
        email: authUser.email,
        nome: authUser.email?.split('@')[0] || 'Usuário (Offline)',
        ultimo_acesso: new Date().toISOString(),
        tipo_usuario: 'usuario',
        ativo: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        offline: true
      } as Usuario
    }
  }

  const checkUser = useCallback(async () => {
    if (!isMounted) return;
    
    try {
      const { data: { user: authUser }, error } = await retryOperation(
        async () => await supabase.auth.getUser(),
        3,
        1000,
        'Verificação de usuário'
      );
      
      if (error) {
        setLoading(false);
        return;
      }
      
      if (authUser) {
        const dbUser = await getOrCreateUser(authUser);
        setUser(dbUser);
      }
    } catch (error) {
      // Se estiver offline, mostra uma mensagem mais amigável
      if (isOffline) {
        toast.error('Você está offline. Algumas funcionalidades podem estar limitadas.');
      } else {
        toast.error('Erro ao conectar com o servidor. Tente novamente mais tarde.');
      }
    } finally {
      setLoading(false);
    }
  }, [isMounted, isOffline]);

  useEffect(() => {
    if (!isMounted) return;
    
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event: string, session: Session | null) => {
      console.log(`[useAuth] Evento de autenticação: ${event}`);
      
      if (session) {
        try {
          const { user: authUser } = session;
          const dbUser = await getOrCreateUser(authUser);
          setUser(dbUser);
          console.log('[useAuth] Usuário autenticado carregado');
          
          // Remover redirecionamento automático - as páginas gerenciam isso
        } catch (error) {
          console.error('[useAuth] Erro ao processar evento de autenticação:', error);
        }
      } else {
        console.log('[useAuth] Usuário não autenticado');
        setUser(null);
        
        // Remover redirecionamento automático - as páginas gerenciam isso
      }
      setLoading(false);
    });

    checkUser();

    return () => {
      subscription.unsubscribe();
    }
  }, [router, checkUser, isMounted]);

  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await retryOperation(
        async () => await supabase.auth.signInWithPassword({
          email,
          password,
        }),
        3,
        1000,
        'Login'
      );

      if (error) {
        // Mensagens de erro mais amigáveis
        if (error.message.includes('Invalid login credentials')) {
          toast.error('Email ou senha incorretos. Tente novamente.');
        } else if (isOffline) {
          toast.error('Você está offline. Não é possível fazer login no momento.');
        } else {
          toast.error('Erro ao fazer login. Tente novamente mais tarde.');
        }
        
        throw error;
      }
      
      // Garantir que o usuário seja carregado após o login bem-sucedido
      if (data && data.user) {
        try {
          const dbUser = await getOrCreateUser(data.user);
          setUser(dbUser);
          
          // Limpar localStorage para evitar problemas com tokens antigos
          if (typeof window !== 'undefined') {
            // Remover flags de redirecionamento para permitir redirecionamento limpo
            sessionStorage.removeItem('recent_auth_redirect');
          }
          
          console.log("Login bem-sucedido no useAuth");
        } catch (loadError) {
          console.error("Erro ao carregar usuário após login:", loadError);
        }
      }
      
      toast.success('Login realizado com sucesso!');
      return data;
    } catch (error) {
      throw error;
    }
  }

  const signOut = async () => {
    try {
      // 1. Limpar localStorage
      if (typeof window !== 'undefined') {
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith('supabase.auth.') || key.startsWith('sb-')) {
            localStorage.removeItem(key);
          }
        });
      }

      // 2. Definir o usuário como null
      setUser(null);
      
      // 3. Fazer o logout no Supabase
      await supabase.auth.signOut({ scope: 'global' });
      
      console.log('[useAuth] Logout realizado com sucesso');
      
      // 4. Redirecionamento será gerenciado pelas páginas através do router
      // Não fazemos redirecionamento aqui
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      
      // 5. Garantir que o usuário seja deslogado mesmo em caso de erro
      setUser(null);
      
      // Limpeza de emergência
      if (typeof window !== 'undefined') {
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith('supabase.auth.') || key.startsWith('sb-')) {
            localStorage.removeItem(key);
          }
        });
      }
    }
  }

  // Não renderiza nada durante a montagem inicial para evitar problemas de hidratação
  if (!isMounted) {
    return null;
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut, isOffline }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}
