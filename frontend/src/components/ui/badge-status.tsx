import { cn } from "@/lib/utils";
import { StatusExecucao } from "@/types/execucao";

interface BadgeStatusProps {
  value: StatusExecucao | string;
  colorScheme?: {
    [key: string]: string;
  };
}

export function BadgeStatus({ value, colorScheme = {} }: BadgeStatusProps) {
  const defaultColors: { [key: string]: string } = {
    pendente: "bg-yellow-50 text-yellow-700 border-yellow-100",
    resolvido: "bg-green-50 text-green-700 border-green-100",
    resolvida: "bg-green-50 text-green-700 border-green-100",
    realizada: "bg-green-50 text-green-700 border-green-100",
    cancelada: "bg-red-50 text-red-700 border-red-100",
    em_andamento: "bg-blue-50 text-blue-700 border-blue-100",
    aguardando: "bg-purple-50 text-purple-700 border-purple-100"
  };

  const colors = { ...defaultColors, ...colorScheme };

  const getDisplayText = (value: string) => {
    const displayMap: { [key: string]: string } = {
      'pendente': 'Pendente',
      'resolvido': 'Resolvido',
      'resolvida': 'Resolvida',
      'realizada': 'Realizada',
      'cancelada': 'Cancelada',
      'em_andamento': 'Em andamento',
      'aguardando': 'Aguardando'
    };
    
    return displayMap[value.toLowerCase()] || value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, " ");
  };

  const getColorClass = (value: string) => {
    return colors[value.toLowerCase()] || "bg-gray-50 text-gray-700 border-gray-100";
  };

  // Se o valor for nulo ou indefinido, usamos o status padrão
  const status = value || 'pendente';

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        getColorClass(status)
      )}
    >
      {getDisplayText(status)}
    </span>
  );
} 