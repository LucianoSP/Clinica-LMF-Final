"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from "@/components/ui/dialog";
import { Card, CardContent } from "@/components/ui/card";
import { formatarData } from "@/lib/utils";
import { SessaoLog } from "@/app/(auth)/unimed/interfaces";
import { RefreshCw, CheckCircle, XCircle, AlertTriangle, Download, Copy, Clock } from "lucide-react";
import { DetailedLogViewer } from "@/components/unimed/LogViewer";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export interface SessaoDetalhesProps {
  sessaoId: string | null;
  logs: SessaoLog[];
  onClose: () => void;
  onReprocessar: (sessaoId: string) => Promise<void>;
}

export function SessaoDetalhes({ sessaoId, logs, onClose, onReprocessar }: SessaoDetalhesProps) {
  const [isReprocessando, setIsReprocessando] = useState(false);
  const [activeTab, setActiveTab] = useState("logs");
  
  if (!sessaoId) return null;

  const handleReprocessar = async () => {
    if (sessaoId) {
      setIsReprocessando(true);
      try {
        await onReprocessar(sessaoId);
      } finally {
        setIsReprocessando(false);
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "sucesso":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "erro":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case "info":
        return <Clock className="h-4 w-4 text-blue-500" />;
      default:
        return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "sucesso":
        return "bg-green-100 text-green-800 border-green-200";
      case "erro":
        return "bg-red-100 text-red-800 border-red-200";
      case "info":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };
  
  const temErros = logs.some(log => log.status === "erro");
  const ultimoLog = logs.length > 0 ? logs[logs.length - 1] : null;
  const dataUltimoLog = ultimoLog ? formatarData(new Date(ultimoLog.created_at), true) : "N/A";
  
  // Agrupar logs por tipo para estatísticas
  const estatisticas = {
    total: logs.length,
    sucesso: logs.filter(log => log.status === "sucesso").length,
    erro: logs.filter(log => log.status === "erro").length,
    info: logs.filter(log => log.status === "info").length,
  };
  
  // Extrair informações da sessão do primeiro log, se disponível
  const sessaoInfo = logs.length > 0 && logs[0].detalhes ? logs[0].detalhes : null;

  return (
    <Dialog open={!!sessaoId} onOpenChange={(open: boolean) => !open && onClose()}>
      <DialogContent className="w-full max-w-3xl overflow-y-auto max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="text-xl">Detalhes da Sessão</DialogTitle>
          <DialogDescription>
            {logs.length} registros de log • Última atualização: {dataUltimoLog}
          </DialogDescription>
        </DialogHeader>
        
        {sessaoInfo && (
          <div className="bg-muted/30 rounded-lg p-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium mb-2">Informações da Guia</h3>
                <dl className="grid grid-cols-2 gap-1 text-sm">
                  <dt className="text-muted-foreground">Número da Guia:</dt>
                  <dd className="font-medium">{sessaoInfo.numero_guia || "N/A"}</dd>
                  
                  <dt className="text-muted-foreground">Paciente:</dt>
                  <dd>{sessaoInfo.paciente_nome || "N/A"}</dd>
                  
                  <dt className="text-muted-foreground">Carteirinha:</dt>
                  <dd>{sessaoInfo.paciente_carteirinha || "N/A"}</dd>
                </dl>
              </div>
              <div>
                <h3 className="text-sm font-medium mb-2">Informações de Processamento</h3>
                <dl className="grid grid-cols-2 gap-1 text-sm">
                  <dt className="text-muted-foreground">ID da Tarefa:</dt>
                  <dd className="font-mono text-xs">{sessaoInfo.task_id || "N/A"}</dd>
                  
                  <dt className="text-muted-foreground">Data de Execução:</dt>
                  <dd>{sessaoInfo.data_execucao ? formatarData(new Date(sessaoInfo.data_execucao)) : "N/A"}</dd>
                  
                  <dt className="text-muted-foreground">Status:</dt>
                  <dd>
                    <Badge variant="outline" className={getStatusBadge(temErros ? "erro" : "sucesso")}>
                      {temErros ? "Com Erro" : "Processado"}
                    </Badge>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        )}
        
        <Tabs defaultValue="logs" value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 mb-4">
            <TabsTrigger value="logs">Logs Detalhados</TabsTrigger>
            <TabsTrigger value="estatisticas">Estatísticas</TabsTrigger>
          </TabsList>
          
          <TabsContent value="logs" className="mt-0">
            <DetailedLogViewer logs={logs} height="300px" />
          </TabsContent>
          
          <TabsContent value="estatisticas" className="mt-0">
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-muted/30 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold">{estatisticas.total}</div>
                    <div className="text-sm text-muted-foreground">Total de Logs</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-700">{estatisticas.sucesso}</div>
                    <div className="text-sm text-green-600">Sucessos</div>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-red-700">{estatisticas.erro}</div>
                    <div className="text-sm text-red-600">Erros</div>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-700">{estatisticas.info}</div>
                    <div className="text-sm text-blue-600">Informações</div>
                  </div>
                </div>
                
                {temErros && (
                  <div className="mt-6">
                    <h3 className="text-sm font-medium mb-2">Erros Encontrados</h3>
                    <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm">
                      <ul className="list-disc pl-5 space-y-1">
                        {logs
                          .filter(log => log.status === "erro")
                          .map((log, index) => (
                            <li key={index} className="text-red-800">
                              {log.mensagem}
                            </li>
                          ))}
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <DialogFooter className="gap-2 sm:gap-0 mt-4">
          {temErros && (
            <Button 
              variant="secondary" 
              onClick={handleReprocessar}
              disabled={isReprocessando}
              className="gap-2"
            >
              {isReprocessando ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Reprocessando...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Reprocessar Sessão
                </>
              )}
            </Button>
          )}
          <Button variant="outline" onClick={onClose}>Fechar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 