import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { ProcessingStatus } from "@/app/(auth)/unimed/interfaces";
import { formatarData } from "@/lib/utils";
import { Activity, Clock, Database, AlertCircle } from "lucide-react";

interface RealTimeMonitorProps {
  processingStatus: ProcessingStatus;
  getStatusColor: (status: string) => string;
  getStatusText: (status: string) => string;
  formatDuration: (startDate: string, endDate: string | null) => string;
}

const RealTimeMonitor = ({
  processingStatus,
  getStatusColor,
  getStatusText,
  formatDuration
}: RealTimeMonitorProps) => {
  if (!processingStatus || !['processing', 'capturing'].includes(processingStatus.status)) return null;
  
  const calculateProgress = (processed: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((processed / total) * 100);
  };
  
  const progress = calculateProgress(processingStatus.processed_guides, processingStatus.total_guides);
  
  return (
    <Card className="border-l-4 border-l-blue-500 shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardContent className="pt-6">
        <div className="flex flex-col space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="relative">
                <span className="absolute inset-0 animate-ping h-3 w-3 bg-blue-500 rounded-full opacity-75"></span>
                <span className="relative h-3 w-3 bg-blue-600 rounded-full"></span>
              </div>
              <h3 className="font-semibold text-lg">Captura em Andamento</h3>
            </div>
            <Badge variant="outline" className={cn("capitalize", getStatusColor(processingStatus.status))}>
              {getStatusText(processingStatus.status)}
            </Badge>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <div className="min-w-0">
                <p className="text-muted-foreground">ID da Tarefa</p>
                <p className="font-mono text-xs truncate" title={processingStatus.task_id}>
                  {processingStatus.task_id}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-muted-foreground">Iniciado em</p>
                <p>{formatarData(new Date(processingStatus.started_at), true)}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <div>
                <p className="text-muted-foreground">Duração</p>
                <p>{formatDuration(processingStatus.started_at, null)}</p>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Progresso: {progress}%</span>
              <span className="text-muted-foreground">{processingStatus.processed_guides} de {processingStatus.total_guides} guias</span>
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
          
          <div className="bg-muted/50 p-3 rounded-md text-sm">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="h-4 w-4 text-blue-500 flex-shrink-0" />
              <p className="font-medium">Detalhes da Execução:</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
              <div>
                <span className="text-muted-foreground">Período:</span>
                <span className="ml-2 font-medium break-words">{processingStatus.start_date} a {processingStatus.end_date}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Máx. Guias:</span>
                <span className="ml-2 font-medium">{processingStatus.max_guides || "Ilimitado"}</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default RealTimeMonitor; 