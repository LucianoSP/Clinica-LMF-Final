import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Inicializar o cliente Supabase
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

export async function GET(request: NextRequest) {
  try {
    const { data, error } = await supabase
      .from('agendamentos_profissionais')
      .select(`
        id,
        schedule_id,
        professional_id,
        agendamentos (id, data_agendamento, hora_inicio),
        usuarios_aba (user_name, user_lastname)
      `)
      .order('id', { ascending: true })
      .limit(100); // Limitando para não sobrecarregar

    if (error) {
      console.error('Erro ao buscar relações agendamentos-profissionais:', error);
      return NextResponse.json(
        { error: 'Erro ao buscar dados de relações agendamentos-profissionais' },
        { status: 500 }
      );
    }

    return NextResponse.json(data || []);
  } catch (error) {
    console.error('Erro na requisição de relações agendamentos-profissionais:', error);
    return NextResponse.json(
      { error: 'Erro interno no servidor' },
      { status: 500 }
    );
  }
} 