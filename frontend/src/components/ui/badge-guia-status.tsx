"use client"

import { cn } from "@/lib/utils";
import { GuiaStatus, TipoGuia } from "@/types/guia";

interface BadgeGuiaStatusProps {
  value: GuiaStatus | TipoGuia;
  colorScheme?: {
    [key in GuiaStatus | TipoGuia]?: string;
  };
}

export function BadgeGuiaStatus({ value, colorScheme = {} }: BadgeGuiaStatusProps) {
  const defaultColors: { [key in GuiaStatus | TipoGuia]: string } = {
    // Status
    rascunho: "bg-gray-50 text-gray-700 border-gray-100",
    pendente: "bg-yellow-50 text-yellow-700 border-yellow-100",
    autorizada: "bg-green-50 text-green-700 border-green-100",
    negada: "bg-red-50 text-red-700 border-red-100",
    cancelada: "bg-red-50 text-red-700 border-red-100",
    executada: "bg-blue-50 text-blue-700 border-blue-100",
    // Tipos
    consulta: "bg-purple-50 text-purple-700 border-purple-100",
    exame: "bg-indigo-50 text-indigo-700 border-indigo-100",
    procedimento: "bg-cyan-50 text-cyan-700 border-cyan-100",
    internacao: "bg-teal-50 text-teal-700 border-teal-100",
  };

  const colors = { ...defaultColors, ...colorScheme };

  const getDisplayText = (value: GuiaStatus | TipoGuia) => {
    return value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, " ");
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-1 text-xs font-medium rounded-md border",
        colors[value]
      )}
    >
      {getDisplayText(value)}
    </span>
  );
}
