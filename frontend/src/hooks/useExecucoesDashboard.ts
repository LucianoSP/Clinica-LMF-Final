import { create } from 'zustand';
import { pacienteService } from '@/services/pacienteService';
import { useQuery } from '@tanstack/react-query';
import { Paciente } from '@/types/paciente';
import { Carteirinha } from '@/types/carteirinha';
import { Guia } from '@/types/guia';
import { StandardResponse, PaginatedResponse } from '@/types/api';

interface ExecucoesDashboardStore {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  selectedPacienteId: string | null;
  setSelectedPacienteId: (id: string | null) => void;
}

export const useExecucoesDashboardStore = create<ExecucoesDashboardStore>((set) => ({
  searchTerm: '',
  setSearchTerm: (term: string) => set({ searchTerm: term }),
  selectedPacienteId: null,
  setSelectedPacienteId: (id: string | null) => set({ selectedPacienteId: id }),
}));

interface DashboardData {
  paciente: Paciente;
  carteirinhas: Carteirinha[];
  guias: Guia[];
}

export function useExecucoesDashboard() {
  const { searchTerm, setSearchTerm, selectedPacienteId, setSelectedPacienteId } = useExecucoesDashboardStore();

  const searchResults = useQuery({
    queryKey: ['pacientes', 'search', searchTerm],
    queryFn: async () => {
      if (searchTerm.length < 3) return { items: [] };
      const response = await pacienteService.buscarPorTermo(searchTerm, {
        fields: "id,nome,cpf,data_nascimento,telefone,email"
      });
      return response;
    },
    enabled: searchTerm.length >= 3,
    select: (data: any) => data?.items || []
  });

  const dashboardData = useQuery<DashboardData | null, Error, DashboardData | null>({
    queryKey: ['pacientes', 'dashboard', selectedPacienteId],
    queryFn: async (): Promise<DashboardData | null> => {
      if (!selectedPacienteId) return null;
      const [pacienteRes, carteirinhasRes, guiasRes] = await Promise.all([
        pacienteService.obter(selectedPacienteId, "id,nome,cpf,data_nascimento,telefone,email"),
        pacienteService.obterCarteirinhas(selectedPacienteId) as Promise<StandardResponse<PaginatedResponse<Carteirinha>>>,
        pacienteService.obterGuias(selectedPacienteId) as Promise<StandardResponse<PaginatedResponse<Guia>>>,
      ]);
      
      if (!pacienteRes.data) {
        throw new Error('Paciente não encontrado');
      }
      
      return {
        paciente: pacienteRes.data,
        carteirinhas: carteirinhasRes.data?.items || [],
        guias: guiasRes.data?.items || [],
      };
    },
    enabled: !!selectedPacienteId,
  });

  return {
    searchTerm,
    setSearchTerm,
    searchResults: {
      data: searchResults.data || [],
      isLoading: searchResults.isLoading
    },
    selectedPacienteId,
    setSelectedPacienteId,
    dashboardData,
  };
} 