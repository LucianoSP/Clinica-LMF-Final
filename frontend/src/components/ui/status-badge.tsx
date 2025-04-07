import { cn } from "@/lib/utils";

type Status = 'pendente' | 'resolvido' | string;

interface StatusBadgeProps {
  status: Status;
}

const statusMap: Record<string, { label: string, className: string }> = {
  pendente: {
    label: 'Pendente',
    className: 'bg-yellow-50 text-yellow-700 border-yellow-100'
  },
  resolvido: {
    label: 'Resolvido',
    className: 'bg-green-50 text-green-700 border-green-100'
  },
  resolvida: {
    label: 'Resolvida',
    className: 'bg-green-50 text-green-700 border-green-100'
  },
  cancelado: {
    label: 'Cancelado',
    className: 'bg-red-50 text-red-700 border-red-100'
  },
  cancelada: {
    label: 'Cancelada',
    className: 'bg-red-50 text-red-700 border-red-100'
  },
  em_andamento: {
    label: 'Em andamento',
    className: 'bg-blue-50 text-blue-700 border-blue-100'
  },
  aguardando: {
    label: 'Aguardando',
    className: 'bg-purple-50 text-purple-700 border-purple-100'
  }
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const statusLower = status.toLowerCase();
  const config = statusMap[statusLower] || {
    label: status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' '),
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