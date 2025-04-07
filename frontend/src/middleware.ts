import { NextResponse, type NextRequest } from 'next/server'

// Middleware que adiciona headers de CORS para requisições externas
export async function middleware(request: NextRequest) {
    // Lista de origens permitidas
    const allowedOrigins = [
        'http://localhost:3000',
        'https://clinicalmf-producao.vercel.app',
        process.env.NEXT_PUBLIC_URL || '',
        process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    ].filter(Boolean);

    // Obtém a origem da requisição
    const origin = request.headers.get('origin') || '';
    const isAllowedOrigin = allowedOrigins.includes(origin) || origin === '';
    
    // Tratamento especial para requisições OPTIONS (preflight)
    if (request.method === 'OPTIONS') {
        const response = new NextResponse(null, { status: 204 });
        
        // Adicionar headers CORS para requisições preflight
        response.headers.set('Access-Control-Allow-Origin', isAllowedOrigin ? origin : allowedOrigins[0]);
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Client-Info, Prefer, Accept, x-api-key, apikey');
        response.headers.set('Access-Control-Allow-Credentials', 'true');
        response.headers.set('Access-Control-Max-Age', '86400'); // 24 horas
        
        return response;
    }
    
    // Verificar se a requisição é para uma rota de API ou para o Supabase
    if (request.nextUrl.pathname.startsWith('/api') || 
        request.nextUrl.href.includes('supabase.co') ||
        request.nextUrl.pathname.startsWith('/supabase-proxy')) {
        
        // Criar uma resposta com os headers CORS adequados
        const response = NextResponse.next();
        
        // Adicionar headers CORS
        response.headers.set('Access-Control-Allow-Origin', isAllowedOrigin ? origin : allowedOrigins[0]);
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Client-Info, Prefer, Accept, x-api-key, apikey');
        response.headers.set('Access-Control-Allow-Credentials', 'true');
        
        return response;
    }
    
    // Verificar autenticação para rotas que exigem login
    const token = request.cookies.get('token')?.value;
    
    // Verifica se é uma rota que precisa de autenticação
    if (request.nextUrl.pathname.startsWith('/pacientes')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        '/api/:path*', 
        '/pacientes/:path*', 
        '/supabase-proxy/:path*',
        '/((?!_next/static|_next/image|favicon.ico).*)'
    ]
};
