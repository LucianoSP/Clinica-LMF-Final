import { NextRequest, NextResponse } from 'next/server';

/**
 * API route para servir como proxy para o Supabase e evitar problemas de CORS
 * Esta rota receberá requisições e as encaminhará para o Supabase
 */
export async function GET(request: NextRequest) {
  return handleSupabaseRequest(request, 'GET');
}

export async function POST(request: NextRequest) {
  return handleSupabaseRequest(request, 'POST');
}

export async function PUT(request: NextRequest) {
  return handleSupabaseRequest(request, 'PUT');
}

export async function PATCH(request: NextRequest) {
  return handleSupabaseRequest(request, 'PATCH');
}

export async function DELETE(request: NextRequest) {
  return handleSupabaseRequest(request, 'DELETE');
}

export async function OPTIONS(request: NextRequest) {
  // Para requisições OPTIONS, retornamos apenas os headers necessários
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, apikey, Prefer',
      'Access-Control-Max-Age': '86400',
      'Access-Control-Allow-Credentials': 'true',
    },
  });
}

/**
 * Função auxiliar para encaminhar as requisições para o Supabase
 */
async function handleSupabaseRequest(request: NextRequest, method: string) {
  try {
    // Extrair os parâmetros da URL e searchParams
    const searchParams = new URLSearchParams(request.nextUrl.searchParams);
    
    // Determinar a rota no Supabase com base nos parâmetros
    let supabasePath = '/rest/v1';
    if (searchParams.has('table')) {
      const table = searchParams.get('table');
      supabasePath += `/${table}`;
      searchParams.delete('table');
    }
    
    // Construir a URL completa do Supabase
    const supabaseUrl = `${process.env.NEXT_PUBLIC_SUPABASE_URL}${supabasePath}`;
    
    // Obter o corpo da requisição, se houver
    let body = null;
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      body = await request.json().catch(() => null);
    }
    
    // Extrair os headers da requisição original
    const headers = new Headers();
    headers.set('Content-Type', 'application/json');
    headers.set('apikey', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '');
    
    // Adicionar Authorization se presente na requisição original
    const authHeader = request.headers.get('Authorization');
    if (authHeader) {
      headers.set('Authorization', authHeader);
    } else {
      headers.set('Authorization', `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`);
    }
    
    // Adicionar outros headers que o Supabase espera
    if (request.headers.has('Prefer')) {
      headers.set('Prefer', request.headers.get('Prefer') || '');
    }
    
    // Fazer a requisição ao Supabase
    const response = await fetch(`${supabaseUrl}?${searchParams.toString()}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });
    
    // Criar resposta com os mesmos status e corpo do Supabase
    let responseBody;
    try {
      responseBody = await response.json();
    } catch (e) {
      responseBody = null;
    }
    
    return NextResponse.json(responseBody, {
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Erro no proxy para Supabase:', error);
    return NextResponse.json(
      { error: 'Erro interno no servidor de proxy' },
      { status: 500 }
    );
  }
} 