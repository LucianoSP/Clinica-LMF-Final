import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Inicializar o cliente Supabase
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

export async function GET(request: NextRequest) {
  try {
    const { data, error } = await supabase
      .from('usuarios_especialidades')
      .select(`
        id,
        usuario_id,
        especialidade_id,
        substituido,
        usuarios_aba (user_name, user_lastname),
        especialidades (nome)
      `)
      .order('id', { ascending: true });

    if (error) {
      console.error('Erro ao buscar relações usuários-especialidades:', error);
      return NextResponse.json(
        { error: 'Erro ao buscar dados de relações usuários-especialidades' },
        { status: 500 }
      );
    }

    return NextResponse.json(data || []);
  } catch (error) {
    console.error('Erro na requisição de relações usuários-especialidades:', error);
    return NextResponse.json(
      { error: 'Erro interno no servidor' },
      { status: 500 }
    );
  }
} 