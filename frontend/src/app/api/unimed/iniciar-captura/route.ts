import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { v4 as uuid } from 'uuid';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { dataInicial, dataFinal, maxGuias } = body;

    if (!dataInicial || !dataFinal) {
      return NextResponse.json(
        { error: 'Datas inicial e final são obrigatórias' },
        { status: 400 }
      );
    }

    // Validar número máximo de guias
    const numMaxGuias = parseInt(maxGuias) || 100;
    if (isNaN(numMaxGuias) || numMaxGuias < 1 || numMaxGuias > 1000) {
      return NextResponse.json(
        { error: 'Número máximo de guias deve estar entre 1 e 1000' },
        { status: 400 }
      );
    }

    // Gerar taskId único
    const taskId = uuid();

    // Criar registro de status de processamento
    const { data, error } = await supabase
      .from('processing_status')
      .insert({
        task_id: taskId,
        status: 'pending',
        total_guides: 0,
        processed_guides: 0,
        start_date: dataInicial,
        end_date: dataFinal,
        max_guides: numMaxGuias,
        started_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) {
      console.error('Erro ao criar registro de status:', error);
      return NextResponse.json(
        { error: 'Erro ao criar registro de status' },
        { status: 500 }
      );
    }

    // Atualizar o status para 'processing'
    await supabase
      .from('processing_status')
      .update({
        status: 'processing'
      })
      .eq('task_id', taskId);

    // Chamar o endpoint de captura
    try {
      // URL relativa ao mesmo servidor
      const capturaUrl = new URL('/api/unimed/capturar', request.url).toString();
      
      const response = await fetch(capturaUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          taskId,
          dataInicial,
          dataFinal,
          maxGuias: numMaxGuias
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Erro ao iniciar a captura: ${errorData.error || response.statusText}`);
      }
      
      console.log(`Captura iniciada com sucesso para o período ${dataInicial} - ${dataFinal} com max ${numMaxGuias} guias`);
    } catch (error) {
      console.error('Erro ao iniciar captura:', error);
      
      // Atualizar o status para 'error'
      await supabase
        .from('processing_status')
        .update({
          status: 'error',
          error: `Falha ao iniciar o processo de captura: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
          error_at: new Date().toISOString()
        })
        .eq('task_id', taskId);
        
      return NextResponse.json(
        { error: 'Falha ao iniciar o processo de captura' },
        { status: 500 }
      );
    }

    // Retornar o taskId para o cliente
    return NextResponse.json({ 
      taskId, 
      message: 'Processo de captura iniciado com sucesso'
    });
    
  } catch (error) {
    console.error('Erro ao processar requisição:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
} 