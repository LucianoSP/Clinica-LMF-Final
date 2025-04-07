"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { StatusCard } from "@/components/unimed/StatusCard";
import { SessoesTable } from "@/components/unimed/SessoesTable";
import { SessaoDetalhes } from "@/components/unimed/SessaoDetalhes";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { 
  CalendarIcon, 
  RefreshCw, 
  BarChart2, 
  ListChecks, 
  Database, 
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowUpCircle,
  Activity
} from "lucide-react";
import { formatarData } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { ptBR } from 'date-fns/locale';
import { format } from "date-fns";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts';
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHeader, TableRow, TableHead } from "@/components/ui/table";
import RealTimeMonitor from "./RealTimeMonitor";

import { 
  ProcessingStatus, 
  DashboardSummary, 
  ExecutionHistory,
  HourlyMetrics,
  UnimedSessao,
  SessaoLog
} from "@/app/(auth)/unimed/interfaces";

// Cores para o gráfico de pizza
const COLORS = ['#4ade80', '#facc15', '#f87171', '#60a5fa'];

// Função para formatar a duração entre duas datas
const formatDuration = (startDate: string, endDate: string | null): string => {
  if (!startDate) return "0s";
  
  const start = new Date(startDate).getTime();
  const end = endDate ? new Date(endDate).getTime() : Date.now();
  
  const durationInMs = end - start;
  
  // Calcula horas, minutos e segundos
  const hours = Math.floor(durationInMs / 3600000);
  const minutes = Math.floor((durationInMs % 3600000) / 60000);
  const seconds = Math.floor((durationInMs % 60000) / 1000);
  
  // Converte para um formato mais legível
  if (hours > 0 && minutes > 0) {
    // Se tiver horas e minutos, não mostra segundos
    return `${hours}h ${minutes}m`;
  } else if (hours > 0) {
    // Se tiver só horas
    return `${hours}h`;
  } else if (minutes > 0) {
    // Se tiver só minutos
    return `${minutes}m`;
  } else {
    // Se tiver só segundos
    return `${seconds}s`;
  }
};

export function Dashboard() {
  const [activeTab, setActiveTab] = useState("monitoramento");
  const [processing, setProcessing] = useState<ProcessingStatus | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [executions, setExecutions] = useState<ExecutionHistory[]>([]);
  const [hourlyMetrics, setHourlyMetrics] = useState<HourlyMetrics[]>([]);
  const [sessoes, setSessoes] = useState<UnimedSessao[]>([]);
  const [sessaoLogs, setSessaoLogs] = useState<SessaoLog[]>([]);
  const [sessaoSelecionada, setSessaoSelecionada] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dataInicial, setDataInicial] = useState<Date | undefined>(undefined);
  const [dataFinal, setDataFinal] = useState<Date | undefined>(undefined);
  const [maxGuias, setMaxGuias] = useState<number>(100);
  const [updateCountdown, setUpdateCountdown] = useState(30);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [reprocessamentoAtivo, setReprocessamentoAtivo] = useState(false);
  const [iniciandoCaptura, setIniciandoCaptura] = useState(false);

  useEffect(() => {
    fetchData();
    
    // Configurar atualização automática
    const interval = setInterval(() => {
      setUpdateCountdown(prev => {
        if (prev <= 1) {
          fetchData();
          return 30;
        }
        return prev - 1;
      });
    }, 1000);
    
    // Inscrever-se para atualizações em tempo real
    const channel = supabase.channel('unimed-updates')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'processing_status'
      }, () => {
        fetchData();
      })
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'unimed_sessoes_capturadas'
      }, () => {
        fetchSessoes();
      })
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'unimed_log_processamento'
      }, () => {
        if (sessaoSelecionada) {
          fetchSessaoLogs(sessaoSelecionada);
        }
      })
      .subscribe();
      
    return () => {
      clearInterval(interval);
      supabase.removeChannel(channel);
    };
  }, [sessaoSelecionada]);
  
  const fetchData = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        fetchProcessingStatus(),
        fetchExecutionHistory(),
        fetchHourlyMetrics(),
        fetchSessoes(),
      ]);
      
      // Calcular métricas de resumo
      calculateSummary();
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchProcessingStatus = async () => {
    const { data } = await supabase
      .from('processing_status')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1);
      
    if (data && data.length > 0) {
      setProcessing(data[0]);
    }
  };
  
  const fetchExecutionHistory = async () => {
    const { data } = await supabase
      .from('processing_status')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(20);
      
    if (data) {
      const history = data.map((item: any) => ({
        ...item,
        duration_seconds: item.completed_at
          ? Math.floor((new Date(item.completed_at).getTime() - new Date(item.started_at).getTime()) / 1000)
          : Math.floor((new Date().getTime() - new Date(item.started_at).getTime()) / 1000)
      }));
      setExecutions(history);
    }
  };
  
  const fetchHourlyMetrics = async () => {
    // Aqui você poderia buscar métricas por hora do banco ou usar os registros existentes
    // para gerar métricas agregadas por hora
    const { data } = await supabase
      .from('processing_status')
      .select('*')
      .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());
      
    if (data) {
      const hourlyData = data.reduce((acc: any[], curr: any) => {
        const hourDate = new Date(curr.created_at);
        const hour = hourDate.setMinutes(0, 0, 0);
        
        const existing = acc.find(x => x.hour === hour);
        
        if (existing) {
          existing.total_executions += 1;
          existing.total_guides += curr.total_guides || 0;
          existing.processed_guides += curr.processed_guides || 0;
          existing.errors += ['error', 'failed'].includes(curr.status) ? 1 : 0;
        } else {
          acc.push({
            hour,
            total_executions: 1,
            total_guides: curr.total_guides || 0,
            processed_guides: curr.processed_guides || 0,
            errors: ['error', 'failed'].includes(curr.status) ? 1 : 0
          });
        }
        
        return acc;
      }, []);
      
      hourlyData.sort((a: any, b: any) => a.hour - b.hour);
      setHourlyMetrics(hourlyData);
    }
  };
  
  const fetchSessoes = async () => {
    const query = supabase
      .from('unimed_sessoes_capturadas')
      .select('*')
      .order('created_at', { ascending: false });
      
    // Aplicar filtro de status, se houver
    if (statusFilter) {
      query.eq('status', statusFilter);
    }
    
    const { data } = await query.limit(100);
    
    if (data) {
      setSessoes(data);
    }
  };

  const fetchSessaoLogs = async (sessaoId: string) => {
    const { data } = await supabase
      .from('unimed_log_processamento')
      .select('*')
      .eq('sessao_id', sessaoId)
      .order('created_at', { ascending: false });

    if (data) {
      setSessaoLogs(data);
    }
  };
  
  const calculateSummary = () => {
    if (!executions.length) return;
    
    const total = executions.length;
    const today = executions.filter(e => 
      new Date(e.created_at).toDateString() === new Date().toDateString()
    ).length;
    
    const totalGuides = executions.reduce((sum, e) => sum + (e.total_guides || 0), 0);
    const processedGuides = executions.reduce((sum, e) => sum + (e.processed_guides || 0), 0);
    
    const successRate = totalGuides > 0 
      ? Math.round((processedGuides / totalGuides) * 100) 
      : 0;
      
    const avgTime = executions
      .filter(e => e.duration_seconds)
      .reduce((sum, e) => sum + (e.duration_seconds || 0), 0) / total;

    // Calcular sessões pendentes e com erro
    const pendingSessions = sessoes.filter(s => s.status === 'pendente').length;
    const errorSessions = sessoes.filter(s => s.status === 'erro').length;
      
    setSummary({
      total_tasks: total,
      tasks_today: today,
      total_guides: totalGuides,
      total_processed: processedGuides,
      success_rate: successRate,
      avg_processing_time: Math.round(avgTime),
      pending_sessions: pendingSessions,
      error_sessions: errorSessions
    });
  };
  
  const handleReprocessar = async (sessaoId: string) => {
    try {
      setReprocessamentoAtivo(true);
      // Chamar a API para reprocessar a sessão
      const response = await fetch(`/api/unimed/reprocessar-sessao`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessaoId }),
      });
      
      if (!response.ok) {
        throw new Error('Erro ao reprocessar sessão');
      }
      
      // Recarregar dados após reprocessamento
      await fetchSessoes();
      if (sessaoSelecionada === sessaoId) {
        await fetchSessaoLogs(sessaoId);
      }
    } catch (error) {
      console.error("Erro ao reprocessar sessão:", error);
      alert("Erro ao reprocessar a sessão. Tente novamente.");
    } finally {
      setReprocessamentoAtivo(false);
    }
  };

  const handleReprocessarLote = async () => {
    try {
      setReprocessamentoAtivo(true);
      const sessoesComErro = sessoes.filter(s => s.status === 'erro').map(s => s.id);
      
      if (sessoesComErro.length === 0) {
        alert("Não há sessões com erro para reprocessar.");
        return;
      }
      
      if (!confirm(`Deseja reprocessar ${sessoesComErro.length} sessões com erro?`)) {
        return;
      }
      
      const response = await fetch('/api/unimed/reprocessar-lote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessaoIds: sessoesComErro }),
      });
      
      if (!response.ok) {
        throw new Error('Erro ao reprocessar sessões em lote');
      }
      
      alert(`Reprocessamento de ${sessoesComErro.length} sessões iniciado.`);
      await fetchSessoes();
    } catch (error) {
      console.error("Erro ao reprocessar sessões em lote:", error);
      alert("Erro ao reprocessar as sessões. Tente novamente.");
    } finally {
      setReprocessamentoAtivo(false);
    }
  };
  
  const iniciarCaptura = async () => {
    if (!dataInicial || !dataFinal) {
      alert("Selecione as datas inicial e final");
      return;
    }
    
    setIniciandoCaptura(true);
    
    try {
      const response = await fetch('/api/unimed/iniciar-captura', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dataInicial: format(dataInicial, 'dd/MM/yyyy'),
          dataFinal: format(dataFinal, 'dd/MM/yyyy'),
          maxGuias
        }),
      });
      
      if (!response.ok) {
        throw new Error('Erro ao iniciar captura');
      }
      
      const data = await response.json();
      
      // Mensagem mais detalhada
      const mensagem = `Captura iniciada com sucesso!\n\nTask ID: ${data.taskId}\nPeríodo: ${format(dataInicial, 'dd/MM/yyyy')} a ${format(dataFinal, 'dd/MM/yyyy')}\nLimite de guias: ${maxGuias}\n\nO processo está sendo executado em segundo plano. Você pode acompanhar o progresso na aba "Monitoramento".`;
      
      alert(mensagem);
      
      // Atualizar dados após iniciar captura
      fetchData();
      setActiveTab("monitoramento");
    } catch (error) {
      console.error("Erro ao iniciar captura:", error);
      alert("Erro ao iniciar a captura. Tente novamente.");
    } finally {
      setIniciandoCaptura(false);
    }
  };
  
  // Função para obter dados do gráfico de pizza
  const getPieData = () => {
    const statusCounts = {
      pendente: 0,
      processado: 0,
      erro: 0
    };
    
    sessoes.forEach(sessao => {
      if (sessao.status in statusCounts) {
        statusCounts[sessao.status as keyof typeof statusCounts]++;
      }
    });
    
    return [
      { name: "Pendentes", value: statusCounts.pendente, color: "#fbbf24" },
      { name: "Processados", value: statusCounts.processado, color: "#22c55e" },
      { name: "Com Erro", value: statusCounts.erro, color: "#ef4444" }
    ];
  };

  // Dados para o gráfico de barras de desempenho por dia
  const getBarData = () => {
    if (!executions.length) return [];
    
    const dateMap = executions.reduce((acc: Record<string, any>, execution) => {
      const dateStr = new Date(execution.created_at).toISOString().split('T')[0];
      
      if (!acc[dateStr]) {
        acc[dateStr] = {
          date: dateStr,
          total: 0,
          success: 0,
          errors: 0
        };
      }
      
      acc[dateStr].total += 1;
      if (execution.status === 'completed') {
        acc[dateStr].success += 1;
      } else if (execution.status === 'error' || execution.status === 'failed') {
        acc[dateStr].errors += 1;
      }
      
      return acc;
    }, {});
    
    return Object.values(dateMap).sort((a: any, b: any) => a.date.localeCompare(b.date));
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
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
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getStatusText = (status: string) => {
    switch (status.toLowerCase()) {
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
      default:
        return status;
    }
  };

  const StatusSummaryCards = () => (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <Card className="border-l-4 border-l-green-500 shadow-sm hover:shadow-md transition-shadow duration-300">
        <CardHeader className="pb-2">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <CardTitle className="text-sm font-medium">Processadas</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-3xl font-bold">{sessoes.filter(s => s.status === 'processado').length}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {summary && (
                  <>Taxa de sucesso: <span className="font-medium">{summary.success_rate}%</span></>
                )}
              </p>
            </div>
            {summary && summary.success_rate > 0 && (
              <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-sm font-medium text-green-800">{summary.success_rate}%</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      <Card className="border-l-4 border-l-yellow-500 shadow-sm hover:shadow-md transition-shadow duration-300">
        <CardHeader className="pb-2">
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-yellow-500" />
            <CardTitle className="text-sm font-medium">Pendentes</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-3xl font-bold">{sessoes.filter(s => s.status === 'pendente').length}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Aguardando processamento
              </p>
            </div>
            {processing && processing.status === 'processing' && (
              <div className="relative h-10 w-10">
                <div className="absolute inset-0 rounded-full bg-yellow-100 animate-ping opacity-75"></div>
                <div className="relative rounded-full h-10 w-10 bg-yellow-200 flex items-center justify-center">
                  <Clock className="h-5 w-5 text-yellow-700" />
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      <Card className="border-l-4 border-l-red-500 shadow-sm hover:shadow-md transition-shadow duration-300">
        <CardHeader className="pb-2">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <CardTitle className="text-sm font-medium">Com Erro</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-3xl font-bold">{sessoes.filter(s => s.status === 'erro').length}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {sessoes.filter(s => s.status === 'erro').length > 0 ? (
                  <Button 
                    variant="link" 
                    size="sm" 
                    onClick={handleReprocessarLote}
                    disabled={reprocessamentoAtivo}
                    className="h-auto p-0 text-xs text-red-600 hover:text-red-800"
                  >
                    {reprocessamentoAtivo ? 'Reprocessando...' : 'Reprocessar todos'}
                  </Button>
                ) : (
                  'Nenhum erro encontrado'
                )}
              </p>
            </div>
            {sessoes.filter(s => s.status === 'erro').length > 0 && (
              <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-red-700" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
  
  return (
    <div className="space-y-8">
      <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="monitoramento">
            <Activity className="h-4 w-4 mr-2" />
            Monitoramento
          </TabsTrigger>
          <TabsTrigger value="sessoes">
            <ListChecks className="h-4 w-4 mr-2" />
            Sessões
          </TabsTrigger>
          <TabsTrigger value="captura">
            <Database className="h-4 w-4 mr-2" />
            Nova Captura
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="monitoramento" className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            <StatusCard 
              status={processing} 
              onRefresh={fetchProcessingStatus} 
              nextUpdateIn={updateCountdown}
            />
            
            {processing && ['processing', 'capturing'].includes(processing.status) && (
              <RealTimeMonitor 
                processingStatus={processing}
                getStatusColor={getStatusColor}
                getStatusText={getStatusText}
                formatDuration={formatDuration}
              />
            )}
          </div>
          
          <StatusSummaryCards />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
              <CardHeader>
                <CardTitle>Atividade nas Últimas 24h</CardTitle>
                <CardDescription>Guias processadas por hora</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                {hourlyMetrics.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    Sem dados para exibir
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={hourlyMetrics}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="hour" 
                        tickFormatter={(hour) => `${hour}h`}
                      />
                      <YAxis />
                      <Tooltip 
                        formatter={(value) => [`${value} guias`, 'Processadas']}
                        labelFormatter={(hour) => `${hour}:00 - ${hour}:59`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="total_executions" 
                        name="Guias Processadas"
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
            
            <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
              <CardHeader>
                <CardTitle>Distribuição por Status</CardTitle>
                <CardDescription>Proporção de sessões por status</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                {sessoes.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    Sem dados para exibir
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getPieData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        nameKey="name"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {getPieData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`${value} sessões`, '']} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>
          
          <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
            <CardHeader>
              <CardTitle>Histórico de Execuções</CardTitle>
              <CardDescription>Últimas tarefas executadas</CardDescription>
            </CardHeader>
            <CardContent>
              {executions.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">
                  Nenhuma execução registrada
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-medium">Status</th>
                        <th className="text-left py-3 px-4 font-medium">ID da Tarefa</th>
                        <th className="text-left py-3 px-4 font-medium">Guias</th>
                        <th className="text-left py-3 px-4 font-medium">Iniciado em</th>
                        <th className="text-left py-3 px-4 font-medium">Duração</th>
                      </tr>
                    </thead>
                    <tbody>
                      {executions.map((execution) => (
                        <tr key={execution.id} className="border-b hover:bg-muted/50">
                          <td className="py-3 px-4">
                            <Badge variant="outline" className={getStatusColor(execution.status)}>
                              {getStatusText(execution.status)}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 font-mono text-xs">{execution.task_id.substring(0, 8)}...</td>
                          <td className="py-3 px-4">
                            <div className="flex flex-col gap-1">
                              <span>{execution.processed_guides} / {execution.total_guides}</span>
                              <Progress 
                                value={Math.round((execution.processed_guides / execution.total_guides) * 100)} 
                                className="h-1" 
                              />
                            </div>
                          </td>
                          <td className="py-3 px-4">{formatarData(new Date(execution.started_at), true)}</td>
                          <td className="py-3 px-4">
                            {execution.duration_seconds 
                              ? `${Math.floor(execution.duration_seconds / 60)}m ${Math.floor(execution.duration_seconds % 60)}s` 
                              : "Em andamento"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="sessoes" className="space-y-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <Button 
              variant="outline" 
              onClick={() => setStatusFilter(null)}
              className={!statusFilter ? "bg-primary text-primary-foreground hover:bg-primary/90" : ""}
            >
              Todas
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setStatusFilter("pendente")}
              className={statusFilter === "pendente" ? "bg-yellow-100 text-yellow-800" : ""}
            >
              Pendentes
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setStatusFilter("processado")}
              className={statusFilter === "processado" ? "bg-green-100 text-green-800" : ""}
            >
              Processados
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setStatusFilter("erro")}
              className={statusFilter === "erro" ? "bg-red-100 text-red-800" : ""}
            >
              Com Erro
            </Button>
            <Button 
              variant="outline" 
              onClick={fetchSessoes}
              className="gap-2"
              disabled={isLoading}
            >
              <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
              Atualizar
            </Button>
          </div>
          
          <SessoesTable 
            sessoes={sessoes} 
            onVerDetalhes={(id) => {
              setSessaoSelecionada(id);
              fetchSessaoLogs(id);
            }} 
            onReprocessar={handleReprocessar}
            isLoading={isLoading} 
          />
          
          <SessaoDetalhes 
            sessaoId={sessaoSelecionada} 
            logs={sessaoLogs}
            onClose={() => setSessaoSelecionada(null)} 
            onReprocessar={handleReprocessar} 
          />
        </TabsContent>
        
        <TabsContent value="captura" className="space-y-6">
          <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
            <CardHeader>
              <CardTitle>Iniciar Nova Captura</CardTitle>
              <CardDescription>
                Configure os parâmetros para iniciar uma nova captura de guias da Unimed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <h3 className="text-sm font-medium">Período de Captura</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm text-muted-foreground">Data Inicial</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              variant="outline"
                              className={cn(
                                "w-full justify-start text-left font-normal",
                                !dataInicial && "text-muted-foreground"
                              )}
                            >
                              <CalendarIcon className="mr-2 h-4 w-4" />
                              {dataInicial ? format(dataInicial, "dd/MM/yyyy") : "Selecione a data"}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0">
                            <Calendar
                              mode="single"
                              selected={dataInicial}
                              onSelect={setDataInicial}
                              initialFocus
                              locale={ptBR}
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm text-muted-foreground">Data Final</label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              variant="outline"
                              className={cn(
                                "w-full justify-start text-left font-normal",
                                !dataFinal && "text-muted-foreground"
                              )}
                            >
                              <CalendarIcon className="mr-2 h-4 w-4" />
                              {dataFinal ? format(dataFinal, "dd/MM/yyyy") : "Selecione a data"}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0">
                            <Calendar
                              mode="single"
                              selected={dataFinal}
                              onSelect={setDataFinal}
                              initialFocus
                              locale={ptBR}
                              disabled={(date) => 
                                dataInicial ? date < dataInicial : false
                              }
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Limite de Guias</label>
                      <span className="text-sm text-muted-foreground">{maxGuias} guias</span>
                    </div>
                    <Input
                      type="range"
                      min="10"
                      max="1000"
                      step="10"
                      value={maxGuias}
                      onChange={(e) => setMaxGuias(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>10</span>
                      <span>500</span>
                      <span>1000</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col justify-between">
                  <div className="bg-muted/30 p-4 rounded-lg space-y-3">
                    <h3 className="text-sm font-medium">Resumo da Captura</h3>
                    <dl className="grid grid-cols-[100px_1fr] gap-1 text-sm">
                      <dt className="text-muted-foreground">Data Inicial:</dt>
                      <dd>{dataInicial ? format(dataInicial, "dd/MM/yyyy") : "Não definida"}</dd>
                      
                      <dt className="text-muted-foreground">Data Final:</dt>
                      <dd>{dataFinal ? format(dataFinal, "dd/MM/yyyy") : "Não definida"}</dd>
                      
                      <dt className="text-muted-foreground">Limite de Guias:</dt>
                      <dd>{maxGuias}</dd>
                      
                      {dataInicial && dataFinal && (
                        <>
                          <dt className="text-muted-foreground">Período:</dt>
                          <dd>{Math.ceil((dataFinal.getTime() - dataInicial.getTime()) / (1000 * 60 * 60 * 24))} dias</dd>
                        </>
                      )}
                    </dl>
                    
                    {processing && ['processing', 'capturing'].includes(processing.status) && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 text-sm text-yellow-800 mt-3">
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4 text-yellow-500" />
                          <span className="font-medium">Captura em andamento</span>
                        </div>
                        <p className="mt-1 ml-6">Aguarde a conclusão antes de iniciar uma nova captura.</p>
                      </div>
                    )}
                  </div>
                  
                  <Button 
                    className="mt-4 w-full gap-2"
                    onClick={iniciarCaptura}
                    disabled={!dataInicial || !dataFinal || iniciandoCaptura || (processing !== null && ['processing', 'capturing'].includes(processing.status))}
                  >
                    {iniciandoCaptura ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Iniciando...
                      </>
                    ) : (
                      <>
                        <Database className="h-4 w-4" />
                        Iniciar Captura
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {executions.length > 0 && (
            <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
              <CardHeader>
                <CardTitle>Histórico de Execuções</CardTitle>
                <CardDescription>
                  Últimas {executions.length} execuções realizadas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-medium">Status</th>
                        <th className="text-left py-3 px-4 font-medium">ID da Tarefa</th>
                        <th className="text-left py-3 px-4 font-medium">Guias</th>
                        <th className="text-left py-3 px-4 font-medium">Iniciado em</th>
                        <th className="text-left py-3 px-4 font-medium">Duração</th>
                      </tr>
                    </thead>
                    <tbody>
                      {executions.map((execution) => (
                        <tr key={execution.id} className="border-b hover:bg-muted/50">
                          <td className="py-3 px-4">
                            <Badge variant="outline" className={getStatusColor(execution.status)}>
                              {getStatusText(execution.status)}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 font-mono text-xs">{execution.task_id.substring(0, 8)}...</td>
                          <td className="py-3 px-4">
                            <div className="flex flex-col gap-1">
                              <span>{execution.processed_guides} / {execution.total_guides}</span>
                              <Progress 
                                value={Math.round((execution.processed_guides / execution.total_guides) * 100)} 
                                className="h-1" 
                              />
                            </div>
                          </td>
                          <td className="py-3 px-4">{formatarData(new Date(execution.started_at), true)}</td>
                          <td className="py-3 px-4">
                            {execution.duration_seconds 
                              ? `${Math.floor(execution.duration_seconds / 60)}m ${Math.floor(execution.duration_seconds % 60)}s` 
                              : "Em andamento"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 