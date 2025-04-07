import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { formatarData } from "@/lib/utils";
import { Activity, Calendar, Clock, Database, CheckCircle, AlertTriangle, BarChart } from "lucide-react";

interface ExecutionStatsProps {
  taskDetails: {
    task_id: string;
    status: string;
    total_guides: number;
    processed_guides: number;
    retry_guides?: number;
    error?: string | null;
    created_at: string;
    started_at: string;
    completed_at?: string | null;
  };
  getStatusColor: (status: string) => string;
  getStatusText: (status: string) => string;
  formatDuration: (startDate: string, endDate: string | null) => string;
}

export function ExecutionStats({ 
  taskDetails, 
  getStatusColor, 
  getStatusText,
  formatDuration
}: ExecutionStatsProps) {
  const calculateProgress = (processed: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((processed / total) * 100);
  };

  const progress = calculateProgress(taskDetails.processed_guides, taskDetails.total_guides);
  
  const getStatusIcon = () => {
    switch (taskDetails.status.toLowerCase()) {
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
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-2">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <div>
            <CardTitle className="text-lg">Detalhes da Execução</CardTitle>
            <CardDescription>
              ID: <span className="font-mono text-xs">{taskDetails.task_id.substring(0, 12)}...</span>
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <Badge variant="outline" className={cn("px-3 py-1", getStatusColor(taskDetails.status))}>
              {getStatusText(taskDetails.status)}
            </Badge>
            <div className="text-sm text-muted-foreground">
              Duração: <span className="font-medium">{formatDuration(taskDetails.started_at, taskDetails.completed_at || null)}</span>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Progresso: {progress}%</span>
              <span>{taskDetails.processed_guides} de {taskDetails.total_guides} guias</span>
            </div>
            <div className="relative pt-1">
              <Progress 
                value={progress} 
                className={cn(
                  "h-2.5 rounded-full overflow-hidden transition-all duration-500 ease-in-out",
                  taskDetails.status === "error" ? "bg-red-200" : ""
                )} 
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Datas</h3>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-muted-foreground">Criado em:</div>
                <div>{formatarData(new Date(taskDetails.created_at), true)}</div>
                <div className="text-muted-foreground">Iniciado em:</div>
                <div>{formatarData(new Date(taskDetails.started_at), true)}</div>
                {taskDetails.completed_at && (
                  <>
                    <div className="text-muted-foreground">Finalizado em:</div>
                    <div>{formatarData(new Date(taskDetails.completed_at), true)}</div>
                  </>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Database className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Estatísticas</h3>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="text-muted-foreground">Total de Guias:</div>
                <div>{taskDetails.total_guides}</div>
                <div className="text-muted-foreground">Processadas:</div>
                <div>{taskDetails.processed_guides}</div>
                {taskDetails.retry_guides && taskDetails.retry_guides > 0 && (
                  <>
                    <div className="text-muted-foreground">Retentativas:</div>
                    <div>{taskDetails.retry_guides}</div>
                  </>
                )}
                <div className="text-muted-foreground">Taxa de Sucesso:</div>
                <div>
                  {taskDetails.total_guides > 0 
                    ? `${Math.round((taskDetails.processed_guides / taskDetails.total_guides) * 100)}%` 
                    : "N/A"}
                </div>
              </div>
            </div>
          </div>

          {taskDetails.error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-800">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                <span className="font-medium">Erro detectado:</span>
              </div>
              <p className="mt-1 ml-6">{taskDetails.error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 