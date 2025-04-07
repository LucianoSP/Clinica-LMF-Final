/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
    domains: ['localhost', 'wpufnegczzdbuztgpxab.supabase.co']
  },
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  experimental: {
    optimizeCss: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
      },
      // Rota de proxy para o Supabase para evitar CORS
      {
        source: '/supabase-proxy/:path*',
        destination: `${process.env.NEXT_PUBLIC_SUPABASE_URL}/:path*`
      }
    ]
  },
  async headers() {
    // Lista de origens permitidas
    const allowedOrigins = [
      'http://localhost:3000',
      'https://clinicalmf-producao.vercel.app',
      process.env.NEXT_PUBLIC_URL,
      process.env.NEXT_PUBLIC_SUPABASE_URL,
    ].filter(Boolean);
    
    return [
      {
        // Adicionando headers para requisições ao Supabase - Específico para OPTIONS preflight
        source: '/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: allowedOrigins.join(',') },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization, X-Client-Info, Prefer, apikey, x-api-key' },
          { key: 'Access-Control-Max-Age', value: '86400' },
        ],
      },
      {
        // Configuração específica para supabase.co
        source: '/supabase-proxy/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: allowedOrigins.join(',') },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS,PATCH' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization, X-Client-Info, Prefer, apikey, x-api-key' },
        ],
      }
    ]
  }
}

module.exports = nextConfig 