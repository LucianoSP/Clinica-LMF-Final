'use client';

import { useState, useEffect } from 'react';
import { AuditoriaHeader } from '@/components/auditoria/AuditoriaHeader';
import { EstatisticasCards } from '@/components/auditoria/EstatisticasCards';
import { Button } from '@/components/ui/button';
import { toast } from "sonner";
import { format } from 'date-fns';
import api from '@/services/api';
import FiltrosAuditoria from '@/components/auditoria/FiltrosAuditoria';
import { AuditoriaResultado, Divergencia } from '@/types/auditoria';
import { StandardResponse, PaginatedResponse } from '@/types/api';
import axios from 'axios';
import { divergenciaService } from '@/services/divergenciaService';
import { useDivergencias } from '@/hooks/useDivergencias';

export default function AuditoriaPage() {
  const [dataInicial, setDataInicial] = useState<string | null>(null);
  const [dataFinal, setDataFinal] = useState<string | null>(null);
  const [statusFiltro, setStatusFiltro] = useState<string>('todos');
  const [tipoDivergencia, setTipoDivergencia] = useState<string>('todos');
  const [prioridade, setPrioridade] = useState<string>('todas');
  const [resultadoAuditoria, setResultadoAuditoria] = useState<AuditoriaResultado | null>(null);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const formatarDataParaAPI = (date: string | null) => {
    if (!date) return '';
    const [ano, mes, dia] = date.split('-');
    return `${dia}/${mes}/${ano}`;
  };

  const { data: divergenciasData, isLoading, refetch } = useDivergencias(
    page,
    perPage,
    dataInicial ? formatarDataParaAPI(dataInicial) : undefined,
    dataFinal ? formatarDataParaAPI(dataFinal) : undefined,
    statusFiltro !== 'todos' ? statusFiltro : undefined,
    tipoDivergencia !== 'todos' ? tipoDivergencia : undefined,
    prioridade !== 'todas' ? prioridade : undefined,
    'data_identificacao',
    'desc'
  );

  const divergencias = divergenciasData?.items || [];
  const totalPages = divergenciasData?.total_pages || 1;
  const totalRecords = divergenciasData?.total || 0;

  const handleAuditoria = async () => {
    try {
      const requestBody = {
        data_inicio: formatarDataParaAPI(dataInicial),
        data_fim: formatarDataParaAPI(dataFinal)
      };

      const { data: result } = await api.post<StandardResponse<AuditoriaResultado>>('/api/auditoria-execucoes/iniciar', requestBody);
      
      if (result.data) {
        setResultadoAuditoria({
          ...result.data,
          total_execucoes: result.data.total_execucoes || 0,
          tempo_execucao: result.data.tempo_execucao || '',
          divergencias_por_tipo: result.data.divergencias_por_tipo || {}
        });
        await refetch();
      }

      toast.success("Auditoria iniciada com sucesso");
    } catch (error) {
      console.error('Erro ao iniciar auditoria:', error);
      toast.error("Falha ao iniciar auditoria");
    }
  };

  const gerarRelatorio = async () => {
    try {
      const params = {
        ...(dataInicial && { data_inicio: formatarDataParaAPI(dataInicial) }),
        ...(dataFinal && { data_fim: formatarDataParaAPI(dataFinal) })
      };

      const response = await api.get<Blob>('/api/auditoria-execucoes/relatorio', { 
        params,
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio-auditoria-${format(new Date(), 'yyyy-MM-dd')}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success("Relatório gerado com sucesso");
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      toast.error("Falha ao gerar relatório");
    }
  };

  const marcarResolvido = async (id: string) => {
    try {
      await api.put(`/api/divergencias/${id}`, { status: 'resolvida' });
      await refetch();
      toast.success("Divergência marcada como resolvida");
    } catch (error) {
      console.error('Erro ao marcar como resolvida:', error);
      toast.error("Falha ao marcar divergência como resolvida");
    }
  };

  useEffect(() => {
    const buscarUltimaAuditoria = async () => {
      try {
        const { data: result } = await api.get<StandardResponse<AuditoriaResultado>>('/api/auditoria-execucoes/ultima');
        if (result.data) {
          setResultadoAuditoria({
            ...result.data,
            total_execucoes: result.data.total_execucoes || 0,
            tempo_execucao: result.data.tempo_execucao || '',
            divergencias_por_tipo: result.data.divergencias_por_tipo || {},
          });
        }
      } catch (error) {
        console.error('Erro ao buscar última auditoria:', error);
      }
    };
    buscarUltimaAuditoria();
  }, []);

  return (
    <div className="flex flex-col gap-6 p-6">
      <AuditoriaHeader />
      <EstatisticasCards resultadoAuditoria={resultadoAuditoria} />
      <FiltrosAuditoria
        dataInicial={dataInicial}
        setDataInicial={setDataInicial}
        dataFinal={dataFinal}
        setDataFinal={setDataFinal}
        statusFiltro={statusFiltro}
        setStatusFiltro={setStatusFiltro}
        tipoDivergencia={tipoDivergencia}
        setTipoDivergencia={setTipoDivergencia}
        prioridade={prioridade}
        setPrioridade={setPrioridade}
        onAuditoria={handleAuditoria}
        onGerarRelatorio={gerarRelatorio}
        loading={isLoading}
        divergencias={divergencias}
        onMarcarResolvido={marcarResolvido}
        pageCount={totalPages}
        pageIndex={page - 1}
        pageSize={perPage}
        totalRecords={totalRecords}
        onPageChange={(newPage) => setPage(newPage + 1)}
        onPageSizeChange={setPerPage}
      />
    </div>
  );
}