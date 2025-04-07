import axios from 'axios';

// Renomeado para apiClient para clareza e evitar conflitos
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para normalizar URLs (Aplicado a apiClient)
apiClient.interceptors.request.use(
  (config) => {
    if (config.url && config.url !== "/" && config.url.endsWith("/")) {
      config.url = config.url.slice(0, -1);
    }
    // Log mais detalhado da requisição
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, { params: config.params });
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros (Aplicado a apiClient)
apiClient.interceptors.response.use(
  (response) => {
    // Log da resposta
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      // data: response.data, // Comentar para não poluir muito o console
    });
    return response;
  },
  (error) => {
    if (error && typeof error === 'object' && 'isAxiosError' in error) {
      console.error('[API Error]', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          // headers: error.config?.headers, // Omitir headers do log por segurança
        },
      });
    } else {
      console.error('[API Unknown Error]', error);
    }
    return Promise.reject(error);
  }
);
