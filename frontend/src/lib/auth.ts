import { supabase } from './supabase';

export const getCurrentUserId = async (): Promise<string> => {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error || !user) {
      console.error('Erro ao obter usuário:', error);
      return 'system';  // Fallback para 'system' se não houver usuário
    }
    return user.id;
  } catch (error) {
    console.error('Erro ao obter usuário:', error);
    return 'system';  // Fallback para 'system' em caso de erro
  }
}; 