import { Progress } from "./progress"
import { cn } from "@/lib/utils"

interface QuantidadeProgressProps {
  autorizada: number;
  executada: number;
}

export function QuantidadeProgress({ autorizada, executada }: QuantidadeProgressProps) {
  const porcentagem = autorizada > 0 ? (executada / autorizada) * 100 : 0;

  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{executada}/{autorizada}</span>
        <span>{Math.round(porcentagem)}%</span>
      </div>
      <Progress 
        value={porcentagem} 
        className={cn(
          "h-2",
          porcentagem >= 100 ? "bg-green-100" : "bg-blue-100",
          porcentagem >= 100 ? "[&>div]:bg-green-600" : "[&>div]:bg-blue-600"
        )}
      />
    </div>
  );
} 