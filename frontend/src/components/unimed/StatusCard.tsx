"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { ProcessingStatus } from "@/app/(auth)/unimed/interfaces";
import { formatarData } from "@/lib/utils";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { CheckCircle, AlertTriangle, Clock, XCircle, Activity, BarChart, Calendar } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export interface StatusCardProps {
  status: ProcessingStatus | null;
  onRefresh: () => void;
  nextUpdateIn: number;
  className?: string;
}

export function StatusCard({ status, onRefresh, nextUpdateIn, className }: StatusCardProps) {
  const [progress, setProgress] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    calculateProgress();
  }, [status]);

  const calculateProgress = () => {
    if (!status || !status.total_guides) {
      setProgress(0);
      return;
    }

    const calculated = Math.round((status.processed_guides / status.total_guides) * 100);
    setProgress(Math.min(calculated, 100));
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await onRefresh();
    setTimeout(() => setRefreshing(false), 500);
  };

  const getStatusText = () => {
    if (!status) return "Sem informações";

    switch (status.status.toLowerCase()) {
      case "completed":
        return "Finalizado";
      case "error":
        return "Erro";
      case "processing":
      case "processando":
        return "Processando";
      case "capturing":
      case "capturando":
        return "Capturando";
      case "waiting":
      case "aguardando":
        return "Aguardando";
      default:
        return status.status;
    }
  };

  const getStatusIcon = () => {
    if (!status) return <Clock className="h-5 w-5 text-gray-500" />;

    switch (status.status.toLowerCase()) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "error":
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case "processing":
      case "processando":
        return <Activity className="h-5 w-5 text-blue-500" />;
      case "capturing":
      case "capturando":
        return <BarChart className="h-5 w-5 text-indigo-500" />;
      case "waiting":
      case "aguardando":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <XCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    if (!status) return "bg-gray-100 text-gray-800 border-gray-200";

    switch (status.status.toLowerCase()) {
      case "completed":
        return "bg-green-100 text-green-800 border-green-200";
      case "error":
        return "bg-red-100 text-red-800 border-red-200";
      case "processing":
      case "processando":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "capturing":
      case "capturando":
        return "bg-indigo-100 text-indigo-800 border-indigo-200";
      case "waiting":
      case "aguardando":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getCardBorderColor = () => {
    if (!status) return "border-gray-200";

    switch (status.status.toLowerCase()) {
      case "completed":
        return "border-l-4 border-l-green-500";
      case "error":
        return "border-l-4 border-l-red-500";
      case "processing":
      case "processando":
        return "border-l-4 border-l-blue-500";
      case "capturing":
      case "capturando":
        return "border-l-4 border-l-indigo-500";
      case "waiting":
      case "aguardando":
        return "border-l-4 border-l-yellow-500";
      default:
        return "border-l-4 border-l-gray-200";
    }
  };

  return (
    <Card className={cn("shadow-sm hover:shadow-md transition-shadow duration-300", getCardBorderColor(), className)}>
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <div>
            <CardTitle className="text-lg">Status do Processamento</CardTitle>
            <CardDescription>
              Última atualização: {status ? formatarData(new Date(status.updated_at), true) : "N/A"}
            </CardDescription>
          </div>
        </div>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleRefresh}
                className={cn("transition-all duration-300", refreshing && "animate-spin")}
              >
                <RefreshCw className="h-4 w-4" />
                <span className="sr-only">Atualizar</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Atualizar dados (próxima em {nextUpdateIn}s)</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Badge variant="outline" className={cn("px-3 py-1", getStatusColor())}>
              {getStatusText()}
            </Badge>
            <div className="text-sm text-muted-foreground">
              Próxima atualização em <span className="font-medium">{nextUpdateIn}s</span>
            </div>
          </div>

          {status && (status.status === "processing" || status.status === "capturing") && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="font-medium">Progresso: {progress}%</span>
                <span>{status.processed_guides} de {status.total_guides} guias</span>
              </div>
              <div className="relative pt-1">
                <Progress value={progress} className="h-2.5 rounded-full overflow-hidden transition-all duration-500 ease-in-out" />
                {progress > 0 && progress < 100 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="h-full w-1 bg-white/20 animate-progress-pulse"></div>
                  </div>
                )}
              </div>
            </div>
          )}

          {status && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">Período</h3>
                </div>
                <div className="grid grid-cols-[100px_1fr] gap-2 text-sm">
                  <div className="text-muted-foreground">Início:</div>
                  <div className="truncate">{status.start_date || "N/A"}</div>
                  <div className="text-muted-foreground">Fim:</div>
                  <div className="truncate">{status.end_date || "N/A"}</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">Estatísticas</h3>
                </div>
                <div className="grid grid-cols-[100px_1fr] gap-2 text-sm">
                  <div className="text-muted-foreground">Total de Guias:</div>
                  <div>{status.total_guides || 0}</div>
                  <div className="text-muted-foreground">Processadas:</div>
                  <div>{status.processed_guides || 0}</div>
                  {status.retry_guides > 0 && (
                    <>
                      <div className="text-muted-foreground">Retentativas:</div>
                      <div>{status.retry_guides}</div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {status && status.error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-800">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                <span className="font-medium">Erro detectado:</span>
              </div>
              <p className="mt-1 ml-6 break-words">{status.error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 