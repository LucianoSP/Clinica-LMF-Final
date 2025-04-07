import { formatarData } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Eye } from "lucide-react";
import { useState } from "react";
import { DetalheDivergencia } from "./DetalheDivergencia";
import { BadgeStatus } from "@/components/ui/badge-status";
import { Divergencia } from "@/types/auditoria";
import { SortableTable, Column } from '@/components/ui/SortableTable';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from "@/lib/utils";

interface TabelaDivergenciasProps {
  divergencias: Divergencia[];
  onMarcarResolvido: (id: string) => void;
  loading?: boolean;
  pageCount: number;
  pageIndex: number;
  pageSize: number;
  totalRecords: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newSize: number) => void;
}

export function TabelaDivergencias({ 
  divergencias, 
  onMarcarResolvido, 
  loading,
  pageCount,
  pageIndex,
  pageSize,
  totalRecords,
  onPageChange,
  onPageSizeChange
}: TabelaDivergenciasProps) {
  const [selectedDivergencia, setSelectedDivergencia] = useState<Divergencia | null>(null);

  const formatarDataDivergencia = (value: unknown): string => {
    if (!value || typeof value !== 'string') return '-';
    try {
      if (value.includes('/')) {
        const [dia, mes, ano] = value.split('/');
        return formatarData(new Date(Number(ano), Number(mes) - 1, Number(dia)));
      }
      return formatarData(new Date(value));
    } catch {
      return '-';
    }
  };

  // Função para formatar o tipo de divergência como texto
  const formatarTipoDivergencia = (value: unknown, item: Divergencia): string => {
    const tipoValue = String(value || item.tipo_divergencia || '');
    
    // Mapeamento de tipos para texto formatado
    const tiposFormatados: Record<string, string> = {
      'execucao_sem_ficha': 'Execução sem Ficha',
      'ficha_sem_execucao': 'Ficha sem Execução',
      'sessao_sem_assinatura': 'Sessão sem Assinatura',
      'data_divergente': 'Data Divergente',
      'guia_vencida': 'Guia Vencida',
      'quantidade_excedida': 'Quantidade Excedida',
      'falta_data_execucao': 'Falta Data Execução',
      'duplicidade': 'Duplicidade'
    };
    
    return tiposFormatados[tipoValue] || tipoValue.charAt(0).toUpperCase() + tipoValue.slice(1).replace(/_/g, ' ');
  };

  // Função para renderizar badges de prioridade
  const renderizarPrioridade = (value: unknown): JSX.Element => {
    const prioridade = String(value || 'MEDIA').toUpperCase();
    
    const classesPrioridade: Record<string, string> = {
      'ALTA': 'bg-red-50 text-red-700 border-red-100',
      'MEDIA': 'bg-yellow-50 text-yellow-700 border-yellow-100',
      'BAIXA': 'bg-blue-50 text-blue-700 border-blue-100'
    };
    
    return (
      <span className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        classesPrioridade[prioridade] || 'bg-gray-50 text-gray-700 border-gray-100'
      )}>
        {prioridade === 'ALTA' ? 'Alta' : prioridade === 'MEDIA' ? 'Média' : prioridade === 'BAIXA' ? 'Baixa' : prioridade}
      </span>
    );
  };

  const columns: Column<Divergencia>[] = [
    {
      key: 'paciente_nome',
      label: 'Paciente',
    },
    {
      key: 'carteirinha',
      label: 'Carteirinha',
      render: (value: unknown) => (value ? String(value) : '-')
    },
    {
      key: 'numero_guia',
      label: 'Guia',
    },
    {
      key: 'codigo_ficha',
      label: 'Código Ficha',
      render: (value: unknown) => (value ? String(value) : '-')
    },
    {
      key: 'data_atendimento',
      label: 'Data Atendimento',
      render: formatarDataDivergencia
    },
    {
      key: 'data_execucao',
      label: 'Data Execução',
      render: formatarDataDivergencia
    },
    {
      key: 'tipo',
      label: 'Tipo',
      render: formatarTipoDivergencia
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => <BadgeStatus value={value as any} />
    },
    {
      key: 'prioridade',
      label: 'Prioridade',
      render: renderizarPrioridade
    },
    {
      key: 'acoes',
      label: 'Ações',
      render: (_, item) => (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSelectedDivergencia(item)}
          className="h-8 w-8 p-0 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-full"
          title="Ver detalhes"
        >
          <Eye className="h-4 w-4" />
        </Button>
      )
    }
  ];

  return (
    <div>
      <SortableTable<Divergencia>
        data={divergencias}
        columns={columns}
        loading={loading}
        pageCount={pageCount}
        pageIndex={pageIndex}
        pageSize={pageSize}
        totalRecords={totalRecords}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />

      <DetalheDivergencia
        divergencia={selectedDivergencia}
        open={!!selectedDivergencia}
        onClose={() => setSelectedDivergencia(null)}
        onResolverClick={() => {
          if (selectedDivergencia) {
            onMarcarResolvido(selectedDivergencia.id);
            setSelectedDivergencia(null);
          }
        }}
      />
    </div>
  );
}