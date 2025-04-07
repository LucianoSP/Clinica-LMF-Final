import { cn } from "@/lib/utils";

type TipoDivergencia = 
  | 'execucao_sem_ficha'
  | 'ficha_sem_execucao'
  | 'sessao_sem_assinatura'
  | 'data_divergente'
  | 'guia_vencida'
  | 'quantidade_excedida'
  | 'falta_data_execucao'
  | 'duplicidade';

interface DivergenciaBadgeProps {
  tipo: TipoDivergencia | string;
}

const tipoMap: Record<string, { label: string, className: string }> = {
  execucao_sem_ficha: {
    label: 'Execução sem Ficha',
    className: 'bg-red-50 text-red-700 border-red-100'
  },
  ficha_sem_execucao: {
    label: 'Ficha sem Execução',
    className: 'bg-orange-50 text-orange-700 border-orange-100'
  },
  sessao_sem_assinatura: {
    label: 'Sessão sem Assinatura',
    className: 'bg-yellow-50 text-yellow-700 border-yellow-100'
  },
  data_divergente: {
    label: 'Data Divergente',
    className: 'bg-blue-50 text-blue-700 border-blue-100'
  },
  guia_vencida: {
    label: 'Guia Vencida',
    className: 'bg-purple-50 text-purple-700 border-purple-100'
  },
  quantidade_excedida: {
    label: 'Quantidade Excedida',
    className: 'bg-pink-50 text-pink-700 border-pink-100'
  },
  falta_data_execucao: {
    label: 'Falta Data Execução',
    className: 'bg-teal-50 text-teal-700 border-teal-100'
  },
  duplicidade: {
    label: 'Duplicidade',
    className: 'bg-indigo-50 text-indigo-700 border-indigo-100'
  }
};

export function DivergenciaBadge({ tipo }: DivergenciaBadgeProps) {
  const config = tipoMap[tipo] || {
    label: tipo,
    className: 'bg-gray-50 text-gray-700 border-gray-100'
  };

  return (
    <span className={cn(
      "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
      config.className
    )}>
      {config.label}
    </span>
  );
} 