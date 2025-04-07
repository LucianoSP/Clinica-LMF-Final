import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const bancoDados = body.banco_dados || 'abalarissa_db';
    
    // URL do backend - verificar se está corretamente configurada
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';
    
    // Chamada para o backend para importar todas as tabelas
    const response = await axios.post(
      `${backendUrl}/importacao/importar-tudo-sistema-aba`,
      { banco_dados: bancoDados },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return NextResponse.json(response.data);
  } catch (error: any) {
    console.error('Erro ao importar tabelas do sistema Aba:', error);
    
    // Se o erro vier da API do backend, retornar a resposta original
    if (error.response) {
      return NextResponse.json(
        error.response.data,
        { status: error.response.status }
      );
    }
    
    // Caso contrário, retornar um erro genérico
    return NextResponse.json(
      { 
        success: false, 
        message: 'Erro ao importar tabelas do sistema Aba',
        erro_detalhes: error.message
      },
      { status: 500 }
    );
  }
} 