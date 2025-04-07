import axios from 'axios';
import { createClient } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabase';

// URLs dos backends - Altere o comentário abaixo para trocar entre local e Replit
// const API_URL = 'https://a8106910-9c81-4331-a271-aadab0642045-00-36fbcv1bfujcf.kirk.replit.dev/'; // Replit
const API_URL = process.env.NEXT_PUBLIC_API_URL;
//const API_URL = 'http://localhost:8000'; // Local
// Criação da instância axios
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptador de erros para evitar poluição do console
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Silencia mensagens de erro específicas no console
    if (error.message === 'Network Error' && !navigator.onLine) {
      // Tratar silenciosamente erros de rede quando offline
      return Promise.reject(new Error('Dispositivo offline'));
    }
    
    return Promise.reject(error);
  }
);

// Função para obter o ID do usuário atual
export const getCurrentUserId = async (): Promise<string> => {
  try {
    if (!supabase) {
      throw new Error('Cliente Supabase não inicializado');
    }
    
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error) throw error;
    if (!user) throw new Error('AuthSessionMissingError: Auth session missing!');
    return user.id;
  } catch (error) {
    // Evitando logs desnecessários no console
    throw error;
  }
};

// Interfaces e endpoints
export interface ListParams {
  page?: number;
  limit?: number;
  search?: string;
  order_column?: string;
  order_direction?: 'asc' | 'desc';
  fields?: string; // Campos a serem retornados, ex: 'id,nome,cpf'
}

// API Fichas
export const apiFichas = {
  listar: async (params: { search?: string; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params.search) searchParams.append('search', params.search);
    if (params.status) searchParams.append('status', params.status);
    return api.get(`/api/fichas?${searchParams}`);
  },
  conferirSessao: (fichaId: string, sessaoId: string) => 
    api.post(`/api/fichas/${fichaId}/sessoes/${sessaoId}/conferir`),
  atualizarSessao: (fichaId: string, sessaoId: string, data: any) => 
    api.put(`/api/fichas/${fichaId}/sessoes/${sessaoId}`, data),
  excluirSessao: (fichaId: string, sessaoId: string) => 
    api.delete(`/api/fichas/${fichaId}/sessoes/${sessaoId}`),
  excluir: (fichaId: string) => 
    api.delete(`/api/fichas/${fichaId}`),
};

export default api;
