import { useState, useEffect } from 'react';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

export default function TestAuth() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [supabase, setSupabase] = useState<SupabaseClient | null>(null);

  useEffect(() => {
    // Inicializa o Supabase apenas no lado do cliente
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    
    if (supabaseUrl && supabaseAnonKey) {
      const supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
        },
      });
      setSupabase(supabaseClient);
    }
  }, []);

  const login = async () => {
    if (!supabase) {
      setMessage('Cliente Supabase não inicializado');
      return;
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      setMessage('Login bem sucedido: ' + JSON.stringify(data, null, 2));
      console.log('Dados do login:', data);
    } catch (error) {
      setMessage('Erro no login: ' + JSON.stringify(error, null, 2));
      console.error('Erro:', error);
    }
  };

  const checkSession = async () => {
    if (!supabase) {
      setMessage('Cliente Supabase não inicializado');
      return;
    }

    try {
      const { data, error } = await supabase.auth.getSession();
      setMessage('Sessão atual: ' + JSON.stringify(data, null, 2));
      console.log('Sessão:', data);
    } catch (error) {
      setMessage('Erro ao verificar sessão: ' + JSON.stringify(error, null, 2));
      console.error('Erro:', error);
    }
  };

  const getUser = async () => {
    if (!supabase) {
      setMessage('Cliente Supabase não inicializado');
      return;
    }

    try {
      const { data: { user }, error } = await supabase.auth.getUser();
      setMessage('Usuário atual: ' + JSON.stringify(user, null, 2));
      console.log('Usuário:', user);
    } catch (error) {
      setMessage('Erro ao obter usuário: ' + JSON.stringify(error, null, 2));
      console.error('Erro:', error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Teste de Autenticação</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ marginRight: '10px' }}
        />
        <input
          type="password"
          placeholder="Senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ marginRight: '10px' }}
        />
        <button onClick={login}>Login</button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={checkSession} style={{ marginRight: '10px' }}>
          Verificar Sessão
        </button>
        <button onClick={getUser}>
          Obter Usuário
        </button>
      </div>

      <pre style={{ 
        background: '#f5f5f5', 
        padding: '10px', 
        borderRadius: '5px',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-all'
      }}>
        {message}
      </pre>
    </div>
  );
} 