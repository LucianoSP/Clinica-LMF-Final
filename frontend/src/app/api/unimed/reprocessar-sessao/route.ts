import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { v4 as uuid } from 'uuid';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { sessaoId } = body;

    if (!sessaoId) {
      return NextResponse.json(
        { error: 'ID da sessão é obrigatório' },
        { status: 400 }
      );
    }

    // Buscar detalhes da sessão
    const { data: sessao, error: sessaoError } = await supabase
      .from('unimed_sessoes_capturadas')
      .select('*')
      .eq('id', sessaoId)
      .single();

    if (sessaoError || !sessao) {
      console.error('Erro ao buscar sessão:', sessaoError);
      return NextResponse.json(
        { error: 'Sessão não encontrada' },
        { status: 404 }
      );
    }

    // Verificar se a sessão está em estado de erro
    if (sessao.status !== 'erro') {
      return NextResponse.json(
        { error: 'Apenas sessões com erro podem ser reprocessadas' },
        { status: 400 }
      );
    }

    // Gerar um novo ID de execução
    const executionId = uuid();

    // Atualizar a sessão para status pendente
    const { error: updateError } = await supabase
      .from('unimed_sessoes_capturadas')
      .update({
        status: 'pendente',
        error_message: null,
        execution_id: executionId,
        updated_at: new Date().toISOString()
      })
      .eq('id', sessaoId);

    if (updateError) {
      console.error('Erro ao atualizar sessão:', updateError);
      return NextResponse.json(
        { error: 'Erro ao atualizar status da sessão' },
        { status: 500 }
      );
    }

    // Adicionar log de reprocessamento
    await supabase
      .from('sessao_logs')
      .insert({
        sessao_id: sessaoId,
        execution_id: executionId,
        message: 'Sessão marcada para reprocessamento',
        level: 'info',
        created_at: new Date().toISOString()
      });

    // Em produção, aqui você enviaria a sessão para uma fila de reprocessamento
    // Exemplo: chamada para o serviço de processamento
    try {
      // Simular chamada para serviço externo
      setTimeout(async () => {
        try {
          // Chamar serviço real de reprocessamento (exemplo do código em produção)
          const response = await fetch('http://localhost:3333/api/unimed/reprocessar', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              sessaoId,
              executionId
            }),
          });
          
          if (!response.ok) {
            throw new Error('Erro ao comunicar com serviço de reprocessamento');
          }
        } catch (error) {
          console.error('Erro na chamada de reprocessamento:', error);
          
          // Atualizar status da sessão para erro novamente
          await supabase
            .from('unimed_sessoes_capturadas')
            .update({
              status: 'erro',
              error_message: 'Falha na comunicação com serviço de reprocessamento',
              updated_at: new Date().toISOString()
            })
            .eq('id', sessaoId);
            
          // Registrar erro no log
          await supabase
            .from('sessao_logs')
            .insert({
              sessao_id: sessaoId,
              execution_id: executionId,
              message: 'Falha na comunicação com serviço de reprocessamento',
              level: 'error',
              created_at: new Date().toISOString()
            });
        }
      }, 100);
      
    } catch (error) {
      console.error('Erro ao iniciar reprocessamento:', error);
      // Em caso de erro, manteremos a sessão como pendente
      // pois o serviço de processamento deve lidar com isso
    }

    return NextResponse.json({
      success: true,
      message: 'Sessão enviada para reprocessamento',
      sessaoId,
      executionId
    });

  } catch (error) {
    console.error('Erro ao processar requisição:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
} 