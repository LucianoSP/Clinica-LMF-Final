import { createBrowserClient } from '@supabase/ssr'
import type { SupabaseClient } from '@supabase/supabase-js'

// Inicializa o cliente Supabase apenas no lado do cliente
let supabaseClient: ReturnType<typeof createBrowserClient> | null = null;

// Variável para controlar tentativas de reconexão
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 3;
const RECONNECT_DELAY = 2000; // 2 segundos

// Verificar se existem tokens expirados no localStorage
const checkAndCleanExpiredTokens = () => {
  if (typeof window === 'undefined') return;
  
  try {
    // Verificar se existe um token expirado
    const expiresAt = localStorage.getItem('supabase.auth.expires_at');
    if (expiresAt) {
      const expiresAtTime = parseInt(expiresAt, 10);
      const now = Math.floor(Date.now() / 1000);
      
      if (expiresAtTime < now) {
        // Token expirado, limpar localStorage relacionado ao Supabase
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith('supabase.auth.') || key.startsWith('sb-')) {
            localStorage.removeItem(key);
          }
        });
        return true; // Tokens foram limpos
      }
    }
    return false; // Nenhum token expirado encontrado
  } catch (error) {
    console.error('Erro ao verificar tokens expirados:', error);
    return false;
  }
};

// Cria um cliente mock para o servidor ou quando offline
const mockClient = {
  auth: {
    getUser: async () => ({ data: { user: null }, error: null }),
    getSession: async () => ({ data: { session: null }, error: null }),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
    signInWithPassword: async () => ({ data: null, error: new Error('Não disponível no momento') }),
    signOut: async () => ({ error: null })
  },
  from: (table: string) => ({
    select: () => ({
      eq: () => ({
        single: async () => ({ data: null, error: new Error('Modo offline') })
      }),
      limit: () => ({
        order: () => ({
          range: async () => ({ data: [], error: null })
        })
      })
    }),
    insert: () => ({
      select: () => ({
        single: async () => ({ data: null, error: new Error('Modo offline') })
      })
    }),
    update: () => ({
      eq: () => ({
        select: () => ({
          single: async () => ({ data: null, error: new Error('Modo offline') })
        })
      })
    })
  })
} as unknown as SupabaseClient;

// Verifica se o navegador está online
const isOnline = () => typeof navigator !== 'undefined' && navigator.onLine;

// Função para criar o cliente Supabase de forma segura
const createClientWithRetry = () => {
  if (typeof window === 'undefined') return null;
  
  try {
    // Verificar e limpar tokens expirados antes de criar o cliente
    const tokensWereCleaned = checkAndCleanExpiredTokens();
    if (tokensWereCleaned) {
      console.log('Tokens expirados foram limpos antes de criar o cliente Supabase');
    }
    
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    
    if (!supabaseUrl || !supabaseAnonKey) return null;
    if (!isOnline()) return null;
    
    // Criar cliente com configurações personalizadas
    const client = createBrowserClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true
      },
      global: {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      }
    });
    
    // Interceptar todas as operações da PostgREST API para corrigir o modo de acesso
    const originalFrom = client.from.bind(client);
    client.from = (table: string) => {
      const builder = originalFrom(table);
      
      // Sobrescrever o método update para garantir que ele use filtros corretos
      const originalUpdate = builder.update.bind(builder);
      builder.update = (values: any, options?: any) => {
        // Se estivermos atualizando a tabela 'usuarios', garantimos que o método seja PATCH
        if (table === 'usuarios') {
          options = { ...options, method: 'PATCH' };
        }
        
        return originalUpdate(values, options);
      };
      
      return builder;
    };
    
    // Estender o método de signOut para limpar todos os tokens
    const originalSignOut = client.auth.signOut.bind(client.auth);
    client.auth.signOut = async (options?: any) => {
      // Limpar todos os tokens relacionados ao Supabase
      if (typeof window !== 'undefined') {
        Object.keys(localStorage).forEach(key => {
          if (key.startsWith('supabase.auth.') || key.startsWith('sb-')) {
            localStorage.removeItem(key);
          }
        });
      }
      
      // Chamar o método original
      return await originalSignOut(options);
    };
    
    return client;
  } catch (error) {
    console.error('Erro ao criar cliente Supabase:', error);
    return null;
  }
};

// Função para tentar reconectar
const tryReconnect = () => {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) return;
  
  reconnectAttempts++;
  
  setTimeout(() => {
    supabaseClient = createClientWithRetry();
    if (supabaseClient) {
      reconnectAttempts = 0;
      console.log('Reconexão com Supabase bem-sucedida');
    } else if (isOnline()) {
      tryReconnect();
    }
  }, RECONNECT_DELAY);
};

// Inicialização segura do cliente
if (typeof window !== 'undefined') {
  try {
    // Inicializa o cliente, mas garante que não gere erros
    supabaseClient = createClientWithRetry();
    
    // Configura listeners para alterações no estado da conexão
    window.addEventListener('online', () => {
      reconnectAttempts = 0;
      if (!supabaseClient) {
        supabaseClient = createClientWithRetry();
        console.log('Cliente Supabase recriado após recuperar conexão');
      }
    });
    
    window.addEventListener('offline', () => {
      console.log('Dispositivo offline - usando cliente mock');
      supabaseClient = null;
    });
    
    // Verificar periodicamente se os tokens expiraram
    setInterval(() => {
      if (checkAndCleanExpiredTokens() && isOnline()) {
        // Se tokens foram limpos, recriar o cliente
        supabaseClient = createClientWithRetry();
        console.log('Cliente Supabase recriado após limpeza de tokens');
      }
    }, 60000); // Verificar a cada minuto
  } catch (e) {
    // Silencia qualquer erro durante a inicialização
    console.error('Erro ao inicializar cliente Supabase:', e);
    supabaseClient = null;
  }
}

// Exporta o cliente Supabase ou uma versão mock para o servidor/offline
export const supabase = supabaseClient || mockClient;
