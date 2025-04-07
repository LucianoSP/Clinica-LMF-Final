import React, { useRef, useEffect, useState } from 'react';
import { Badge } from "@/components/ui/badge";
import { formatarData } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { SessaoLog } from "@/app/(auth)/unimed/interfaces";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, Info, XCircle, Download, Copy, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogViewerProps {
  logs: string[];
  title?: string;
  height?: string;
  autoScroll?: boolean;
}

export function LogViewer({ logs, title = "Logs", height = "300px", autoScroll = true }: LogViewerProps) {
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);
  
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);
  
  const copyLogs = () => {
    navigator.clipboard.writeText(logs.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const downloadLogs = () => {
    const element = document.createElement("a");
    const file = new Blob([logs.join('\n')], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `logs_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };
  
  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="py-3 flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base font-medium">{title}</CardTitle>
          <CardDescription>{logs.length} entradas</CardDescription>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={copyLogs}
            className="h-8 px-2"
          >
            {copied ? <CheckCircle className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
            {copied ? "Copiado" : "Copiar"}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={downloadLogs}
            className="h-8 px-2"
          >
            <Download className="h-4 w-4 mr-1" />
            Baixar
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div 
          ref={logContainerRef}
          className="overflow-auto text-sm font-mono bg-muted/30 rounded-md"
          style={{ height }}
        >
          {logs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Nenhum log disponível
            </div>
          ) : (
            <div className="p-3 space-y-1.5">
              {logs.map((log, index) => (
                <div 
                  key={index} 
                  className={cn(
                    "py-1 px-2 rounded flex items-start gap-2",
                    log.includes('ERROR') && "bg-red-50 text-red-800",
                    log.includes('WARNING') && "bg-yellow-50 text-yellow-800",
                    log.includes('INFO') && "bg-blue-50 text-blue-800"
                  )}
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {log.includes('ERROR') && <XCircle className="h-4 w-4 text-red-500" />}
                    {log.includes('WARNING') && <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                    {log.includes('INFO') && <Info className="h-4 w-4 text-blue-500" />}
                  </div>
                  <div className="flex-1 break-words">
                    {log}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface DetailedLogViewerProps {
  logs: SessaoLog[];
  title?: string;
  height?: string;
  autoScroll?: boolean;
}

export function DetailedLogViewer({ logs, title = "Logs Detalhados", height = "400px", autoScroll = true }: DetailedLogViewerProps) {
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);
  
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);
  
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'erro':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'sucesso':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Info className="h-4 w-4 text-blue-500" />;
    }
  };
  
  const getStatusClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'erro':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'sucesso':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };
  
  const copyLogs = () => {
    navigator.clipboard.writeText(logs.map(log => log.mensagem).join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const downloadLogs = () => {
    const content = logs.map(log => 
      `[${new Date(log.created_at).toLocaleString()}] [${log.status}] ${log.mensagem}`
    ).join('\n');
    
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `logs_detalhados_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };
  
  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="py-3 flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base font-medium">{title}</CardTitle>
          <CardDescription>{logs.length} registros</CardDescription>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={copyLogs}
            className="h-8 px-2"
          >
            {copied ? <CheckCircle className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
            {copied ? "Copiado" : "Copiar"}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={downloadLogs}
            className="h-8 px-2"
          >
            <Download className="h-4 w-4 mr-1" />
            Baixar
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div 
          ref={logContainerRef}
          className="overflow-auto text-sm"
          style={{ height }}
        >
          {logs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Nenhum log disponível
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-muted/30 sticky top-0">
                <tr>
                  <th className="text-left py-2 px-3 font-medium text-xs">Timestamp</th>
                  <th className="text-left py-2 px-3 font-medium text-xs">Status</th>
                  <th className="text-left py-2 px-3 font-medium text-xs">Mensagem</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr 
                    key={index} 
                    className={cn(
                      "border-b hover:bg-muted/20",
                      log.status === "error" && "bg-red-50/50",
                      log.status === "warning" && "bg-yellow-50/50",
                      log.status === "success" && "bg-green-50/50",
                      log.status === "info" && "bg-blue-50/50"
                    )}
                  >
                    <td className="py-2 px-3 text-xs text-muted-foreground whitespace-nowrap">
                      {log.created_at ? new Date(log.created_at).toLocaleString('pt-BR') : '-'}
                    </td>
                    <td className="py-2 px-3">
                      <Badge 
                        variant="outline" 
                        className={cn(
                          "text-xs font-normal",
                          log.status === "error" && "bg-red-100 text-red-800 hover:bg-red-100",
                          log.status === "warning" && "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
                          log.status === "success" && "bg-green-100 text-green-800 hover:bg-green-100",
                          log.status === "info" && "bg-blue-100 text-blue-800 hover:bg-blue-100"
                        )}
                      >
                        {log.status === "error" && "Erro"}
                        {log.status === "warning" && "Alerta"}
                        {log.status === "success" && "Sucesso"}
                        {log.status === "info" && "Info"}
                      </Badge>
                    </td>
                    <td className="py-2 px-3 break-words">
                      <div className="max-w-2xl">{log.mensagem}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
