import { cn } from "@/lib/utils";
import { StatusFicha } from "@/types/ficha";

interface BadgeFichaStatusProps {
  value: StatusFicha;
  colorScheme?: {
    [key in StatusFicha]?: string;
  };
}

export function BadgeFichaStatus({ value, colorScheme = {} }: BadgeFichaStatusProps) {
  const defaultColors: { [key in StatusFicha]: string } = {
    pendente: "bg-yellow-50 text-yellow-700 border-yellow-100",
    conferida: "bg-green-50 text-green-700 border-green-100",
    faturada: "bg-blue-50 text-blue-700 border-blue-100",
    cancelada: "bg-red-50 text-red-700 border-red-100",
  };

  const colors = { ...defaultColors, ...colorScheme };

  const getDisplayText = (value: StatusFicha) => {
    return value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, " ");
  };

  const getColorClass = (value: StatusFicha) => {
    return colors[value] || "bg-gray-50 text-gray-700 border-gray-100";
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold",
        getColorClass(value)
      )}
    >
      {getDisplayText(value)}
    </span>
  );
}
