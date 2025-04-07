import { cn } from "@/lib/utils";
import { BiometriaStatus } from "@/types/execucao";

interface BadgeBiometriaProps {
    value: BiometriaStatus | undefined | null;
}

const statusConfig = {
    nao_verificado: {
        label: "Não Verificado",
        className: "bg-yellow-50 text-yellow-700 border-yellow-100"
    },
    verificado: {
        label: "Verificado",
        className: "bg-green-50 text-green-700 border-green-100"
    },
    falha: {
        label: "Falha",
        className: "bg-red-50 text-red-700 border-red-100"
    }
} as const;

export function BadgeBiometria({ value }: BadgeBiometriaProps) {
    // Se o valor for nulo ou indefinido, usamos o status padrão
    const status = value || 'nao_verificado';
    
    // Valor padrão caso o status seja inválido
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.nao_verificado;

    return (
        <span
            className={cn(
                "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold",
                config.className
            )}
        >
            {config.label}
        </span>
    );
}