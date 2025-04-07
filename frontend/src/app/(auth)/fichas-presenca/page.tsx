'use client';

import { useState, useEffect } from 'react';
import { PacienteInfoCard } from '@/components/pacientes/paciente-info-card';
import { PacienteStats } from '@/components/pacientes/paciente-stats';
import { PacienteCarteirinhas } from '@/components/pacientes/paciente-carteirinhas';
import { PacienteGuias } from '@/components/pacientes/paciente-guias';
import { PacienteFichas } from '@/components/pacientes/paciente-fichas';
import { usePacienteDashboardStore } from '@/hooks/usePacienteDashboard';
import { Skeleton } from '@/components/ui/skeleton';
import { useFichasPorPaciente } from '@/hooks/useFichas';
import { ComboboxField } from '@/components/ui/combobox-field';
import { pacienteService } from '@/services/pacienteService';
import type { Paciente } from '@/types/paciente';
import { useForm } from 'react-hook-form';
import { Form } from '@/components/ui/form';

interface FormValues {
  paciente: string;
}

export default function FichasPresencaPage() {
  const {
    selectedPacienteId,
    setSelectedPacienteId,
    dashboardData,
  } = usePacienteDashboardStore();

  const form = useForm<FormValues>({
    defaultValues: {
      paciente: ''
    }
  });

  const handleSearch = async (searchTerm: string) => {
    try {
      const response = await pacienteService.buscarPorTermo(searchTerm, {
        fields: "*"
      });
      return response.items || [];
    } catch (error) {
      console.error('Erro na busca de pacientes:', error);
      return [];
    }
  };

  const handleSelect = (paciente: Paciente | null) => {
    setSelectedPacienteId(paciente?.id || null);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold mb-6">Pacientes</h1>

        <div className="max-w-xl">
          <Form {...form}>
            <ComboboxField<Paciente>
              name="paciente"
              label="Buscar Paciente"
              placeholder="Digite o nome ou CPF do paciente..."
              onSearch={handleSearch}
              onSelect={handleSelect}
              getOptionLabel={(paciente) => {
                const label = paciente.nome;
                return paciente.cpf ? `${label} - ${paciente.cpf}` : label;
              }}
              getOptionValue={(paciente) => paciente.id}
            />
          </Form>
        </div>
      </div>

      {dashboardData.isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#8B4513]" />
        </div>
      ) : dashboardData.data ? (
        <div className="flex flex-col gap-6">
          {dashboardData.data?.paciente && (
            <PacienteInfoCard 
              paciente={dashboardData.data.paciente} 
              onClose={() => setSelectedPacienteId(null)}
            />
          )}
          <PacienteStats stats={dashboardData.data.stats} />
          <div className="flex flex-col gap-6">
            <PacienteCarteirinhas
              carteirinhas={dashboardData.data?.carteirinhas || []}
              onViewCarteirinha={(carteirinha) => console.log(carteirinha)}
            />
            <PacienteGuias
              guias={dashboardData.data?.guias || []}
              onViewGuia={(guia) => console.log(guia)}
            />
            {selectedPacienteId && (
              <PacienteFichas
                pacienteId={selectedPacienteId}
                onViewFicha={(ficha) => console.log(ficha)}
              />
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}