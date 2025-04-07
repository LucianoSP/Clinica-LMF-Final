import { cn } from "@/lib/utils";
import { CarteirinhaStatus } from "@/types/carteirinha";

interface BadgeCarteirinhaStatusProps {
  value: CarteirinhaStatus;
  colorScheme?: {
    [key in CarteirinhaStatus]?: string;
  };
}

export function BadgeCarteirinhaStatus({ value, colorScheme = {} }: BadgeCarteirinhaStatusProps) {
  const defaultColors: { [key in CarteirinhaStatus]: string } = {
    ativa: "bg-green-50 text-green-700 border-green-100",
    inativa: "bg-red-50 text-red-700 border-red-100",
    suspensa: "bg-yellow-50 text-yellow-700 border-yellow-100",
    vencida: "bg-gray-50 text-gray-700 border-gray-100",
  };

  const colors = { ...defaultColors, ...colorScheme };

  const getDisplayText = (value: CarteirinhaStatus) => {
    return value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, " ");
  };

  const getColorClass = (value: CarteirinhaStatus) => {
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
