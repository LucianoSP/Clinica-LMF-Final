"use client";

import { useState, useEffect } from "react";
import { Agendamento } from "@/types/agendamento";
import { useAgendamentos } from "@/hooks/useAgendamentos";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown, Database, Loader2, RefreshCcw, Wrench, AlertTriangle, CheckCircle2, XCircle, Filter, Link2 } from "lucide-react";
import { SortableTableWithColumnSelector, Column } from "@/components/ui/SortableTableWithColumnSelector";
import { useDebounce } from "@/hooks/useDebounce";
import { agendamentoService } from "@/services/agendamentoService";
import { vinculacaoService } from "@/services/vinculacaoService";
import { useToast } from "@/components/ui/use-toast";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import Link from "next/link";
import * as XLSX from 'xlsx';
import { formatarData } from "@/lib/utils";
import { Label } from "@/components/ui/label";
import axios from "axios";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Valores fixos para a importação que serão usados internamente
const BANCO_DADOS_PADRAO = "abalarissa_db";
const TABELA_PADRAO = "ps_schedule";

export default function AgendamentosPage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [statusVinculacaoFilter, setStatusVinculacaoFilter] = useState<string>("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedAgendamento, setSelectedAgendamento] = useState<Agendamento | undefined>();
    const [orderColumn, setOrderColumn] = useState("data_agendamento");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("desc");
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [agendamentoToDelete, setAgendamentoToDelete] = useState<string | null>(null);

    // Estado para o modal de importação
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);
    const [dataInicial, setDataInicial] = useState<string>(() => {
        // Define a data inicial como 30 dias atrás por padrão
        const dataAtras = new Date();
        dataAtras.setDate(dataAtras.getDate() - 30);
        return dataAtras.toISOString().split('T')[0]; // Formato YYYY-MM-DD para input type="date"
    });
    const [dataFinal, setDataFinal] = useState<string>(() => {
        // Define a data final como 7 dias à frente por padrão
        const dataFrente = new Date();
        dataFrente.setDate(dataFrente.getDate() + 7);
        return dataFrente.toISOString().split('T')[0]; // Formato YYYY-MM-DD para input type="date"
    });
    const [isImporting, setIsImporting] = useState(false);
    const [isCheckingCount, setIsCheckingCount] = useState(false);
    const [recordCount, setRecordCount] = useState<number | null>(null);
    const [showImportConfirmation, setShowImportConfirmation] = useState(false);
    const [importStatus, setImportStatus] = useState<string>("");
    const [importProgress, setImportProgress] = useState<number>(0);
    const [importResult, setImportResult] = useState<{
        message: string;
        importados: number;
        total: number;
        total_atualizados?: number;
        total_erros?: number;
        erros: Array<string | { agendamento: string, erro: string }>;
        success: boolean;
        connection_status: {
            success: boolean;
            message: string;
        };
        data_inicial?: string;
    } | null>(null);

    // *** NOVO ESTADO PARA CARREGAMENTO DA VINCULAÇÃO ***
    const [isLinking, setIsLinking] = useState(false);

    const debouncedSearch = useDebounce(search, 500);
    const debouncedStatusFilter = useDebounce(statusVinculacaoFilter, 300);

    const { data, isLoading, refetch } = useAgendamentos(
        page,
        limit,
        debouncedSearch,
        orderColumn,
        orderDirection,
        debouncedStatusFilter
    );

    const { toast } = useToast();

    const handleEdit = (agendamento: Agendamento) => {
        setSelectedAgendamento(agendamento);
        setIsModalOpen(true);
    };

    const handleDelete = async (id: string) => {
        setAgendamentoToDelete(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!agendamentoToDelete) return;

        try {
            const response = await agendamentoService.excluir(agendamentoToDelete);
            if (response.success) {
                toast({
                    title: "Agendamento excluído",
                    description: "Agendamento excluído com sucesso!",
                    variant: "default",
                });
                refetch();
            } else {
                toast({
                    title: "Erro ao excluir",
                    description: `Erro ao excluir: ${response.message}`,
                    variant: "destructive",
                });
            }
        } catch (err) {
            console.error("Erro ao excluir agendamento:", err);
            toast({
                title: "Erro ao excluir",
                description: "Não foi possível excluir o agendamento",
                variant: "destructive",
            });
        } finally {
            setIsDeleteDialogOpen(false);
            setAgendamentoToDelete(null);
        }
    };

    const handleExportToExcel = () => {
        try {
            if (!data?.items || data.items.length === 0) {
                toast({
                    title: "Erro ao exportar",
                    description: "Não há dados para exportar",
                    variant: "destructive",
                });
                return;
            }

            // Mapear os dados para um formato mais adequado para Excel
            const dataForExcel = data.items.map(agendamento => ({
                ID: agendamento.id,
                'Nome do Paciente': agendamento.paciente_nome || 'N/A',
                'Procedimento': agendamento.procedimento_nome || 'N/A',
                'Data': formatarData(agendamento.data_agendamento),
                'Hora Início': agendamento.hora_inicio,
                'Hora Fim': agendamento.hora_fim,
                'Status': agendamento.status,
                'Observações': agendamento.observacoes || ''
            }));

            // Criar uma nova planilha
            const worksheet = XLSX.utils.json_to_sheet(dataForExcel);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, "Agendamentos");

            // Gerar o arquivo e forçar o download
            const date = new Date().toISOString().split('T')[0];
            XLSX.writeFile(workbook, `agendamentos_${date}.xlsx`);
            
            toast({
                title: "Dados exportados",
                description: "Dados exportados com sucesso!",
                variant: "default",
            });
        } catch (err) {
            console.error("Erro ao exportar dados:", err);
            toast({
                title: "Erro ao exportar",
                description: "Erro ao exportar dados",
                variant: "destructive",
            });
        }
    };
    
    // Função para verificar a contagem de registros antes da importação
    const checkRecordCount = async () => {
        setIsCheckingCount(true);
        setRecordCount(null);
        
        try {
            const result = await agendamentoService.verificarQuantidadeAgendamentos(
                BANCO_DADOS_PADRAO, 
                TABELA_PADRAO,
                dataInicial,
                dataFinal
            );
            
            setRecordCount(result.quantidade);

            // Sempre mostrar a confirmação após verificar a quantidade
            setShowImportConfirmation(true); 
        } catch (error) {
            console.error("Erro ao verificar quantidade de registros:", error);
            toast({
                title: "Erro",
                description: "Não foi possível verificar a quantidade de registros a importar.",
                variant: "destructive",
            });
        } finally {
            setIsCheckingCount(false);
        }
    };
    
    const handleImportAgendamentos = async () => {
        setIsImporting(true);
        setImportResult(null);
        setShowImportConfirmation(false);
        setImportStatus("Iniciando importação...");
        setImportProgress(10);
        
        try {
            // Simular progresso durante a importação
            const progressInterval = setInterval(() => {
                setImportProgress((prev) => {
                    // Aumentar o progresso gradualmente até 90%
                    const newProgress = prev + Math.floor(Math.random() * 5) + 1;
                    if (newProgress >= 90) {
                        clearInterval(progressInterval);
                        return 90;
                    }
                    
                    // Atualizar mensagens de status com base no progresso
                    if (newProgress > 75) {
                        setImportStatus("Finalizando importação...");
                    } else if (newProgress > 50) {
                        setImportStatus("Processando registros...");
                    } else if (newProgress > 25) {
                        setImportStatus("Importando agendamentos...");
                    }
                    
                    return newProgress;
                });
            }, 800);
            
            // Nova chamada de serviço para usar data específica em vez de período em semanas
            const result = await agendamentoService.importarAgendamentosDesdeData(
                BANCO_DADOS_PADRAO,
                TABELA_PADRAO,
                dataInicial,
                dataFinal
            );
            
            // Limpar o intervalo quando a importação terminar
            clearInterval(progressInterval);
            setImportProgress(100);
            setImportStatus("Importação concluída!");
            setImportResult(result);
            
            if (result.success) {
                const mensagem = result.total_atualizados && result.total_atualizados > 0
                    ? `Importação concluída: ${result.importados - (result.total_atualizados || 0)} novos e ${result.total_atualizados} atualizados de ${formatarData(dataInicial)} até ${formatarData(dataFinal || '')}`
                    : `Importação concluída: ${result.importados} de ${result.total} agendamentos importados de ${formatarData(dataInicial)} até ${formatarData(dataFinal || '')}`;
                
                toast({
                    title: "Importação concluída",
                    description: mensagem,
                    variant: "default",
                });
            } else {
                setImportStatus("Falha na importação");
                toast({
                    title: "Falha na importação",
                    description: `Falha na importação: ${result.message}`,
                    variant: "destructive",
                });
            }
            
            // Atualizar a lista após importação bem-sucedida
            refetch();
        } catch (error) {
            console.error("Erro na importação:", error);
            setImportStatus("Erro na importação");
            setImportProgress(0);
            toast({
                title: "Erro ao importar",
                description: "Erro ao importar agendamentos",
                variant: "destructive",
            });
        } finally {
            // Não fechar o modal automaticamente para mostrar o resultado
            // setIsImporting(false) será chamado quando o usuário fechar o modal
        }
    };

    const handlePageChange = (newPage: number) => {
        setPage(newPage + 1); // +1 porque a API espera páginas começando em 1, mas o componente usa 0-indexed
    };

    const handlePageSizeChange = (newSize: number) => {
        setLimit(newSize);
        setPage(1); // Voltar para a primeira página ao mudar o tamanho
    };

    // Adicionar função para corrigir mapeamentos - simplificada ao máximo
    const handleCorrigirMapeamentos = async () => {
        try {
            // Mostrar toast de carregamento
            toast({
                title: "Corrigindo mapeamentos",
                description: "Por favor, aguarde...",
            });
            
            // Chamar diretamente o backend
            const response = await axios.get("http://localhost:8000/api/importacao/corrigir-agendamentos-importados");
            
            // Resposta bem sucedida
            toast({
                title: "Mapeamentos corrigidos",
                description: "Os mapeamentos foram corrigidos com sucesso!",
                variant: "default",
            });
            
            // Recarregar a lista após corrigir os mapeamentos
            refetch();
        } catch (error) {
            console.error("Erro ao corrigir mapeamentos:", error);
            toast({
                title: "Erro",
                description: "Ocorreu um erro ao tentar corrigir os mapeamentos. Verifique o console para detalhes.",
                variant: "destructive",
            });
        }
    };

    // *** NOVA FUNÇÃO PARA CHAMAR A API DE VINCULAÇÃO BATCH ***
    const handleVincularAgendamentos = async () => {
        setIsLinking(true);
        toast({
            title: "Iniciando Vinculação Automática",
            description: "Tentando vincular agendamentos, sessões e execuções...",
        });

        try {
            // Chamar o serviço real
            const result = await vinculacaoService.vincularAgendamentosBatch();

            if (result.details) { // Verificar se os detalhes foram retornados
                const details = result.details;
                toast({
                    title: "Vinculação Concluída",
                    // Usar a mensagem da API se disponível, senão montar uma
                    description: result.message || `Sessões: ${details.total_vinculado_sessao}, Execuções: ${details.total_vinculado_execucao}.`,
                    variant: "default",
                });
                refetch(); // Recarrega a tabela para mostrar os novos status
            } else {
                // Caso a API retorne sucesso mas sem detalhes (pode acontecer se nada foi vinculado)
                 toast({
                    title: "Vinculação Executada",
                    description: result.message || "Nenhum novo vínculo automático encontrado.",
                    variant: "default",
                });
                refetch();
                // Considerar se um erro deve ser lançado aqui ou se apenas a mensagem é suficiente
                // throw new Error(result.message || "Falha ao executar vinculação batch (sem detalhes)");
            }
        } catch (error: any) {
            console.error("Erro ao vincular agendamentos:", error);
            toast({
                title: "Erro na Vinculação",
                description: error.message || "Não foi possível completar a vinculação automática.",
                variant: "destructive",
            });
        } finally {
            setIsLinking(false);
        }
    };

    // Definição das colunas para a tabela - REORDENADO E AJUSTADO
    const columns: Column<Agendamento>[] = [
        // Colunas Visíveis por Padrão (na ordem solicitada)
        {
            key: "id_atendimento",
            label: "Id Atendimento",
            render: (_, item) => item.id_atendimento || item.id_origem || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "local_nome",
            label: "Unidade/Local",
            render: (_, item) => item.local_nome || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "carteirinha_numero",
            label: "Carteirinha",
            render: (_, item) => item.carteirinha_numero || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "cod_paciente",
            label: "Cod. Paciente (ABA)",
            render: (_, item) => item.id_origem || item.cod_paciente || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "paciente_nome",
            label: "Paciente",
            render: (_, item) => {
                const pacienteNome = item.paciente_nome || "-";
                return (
                    <span className="font-medium">
                        {pacienteNome}
                    </span>
                );
            },
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "plano_saude_nome",
            label: "Plano de Saúde",
            render: (_, item) => item.plano_saude_nome || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "tipo_pagamento_nome",
            label: "Tipo Pagamento",
            render: (value, item) => item.tipo_pagamento_nome || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "data_agendamento",
            label: "Data",
            render: (_, item) => formatarData(item.data_agendamento),
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "hora_inicio",
            label: "Hora inicial",
            render: (_, item) => item.hora_inicio,
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "sala_nome",
            label: "Sala",
            render: (_, item) => item.sala_nome || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "schedule_profissional_id",
            label: "ID Profissional (ABA)",
            render: (_, item) => item.schedule_profissional_id || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "profissional_nome",
            label: "Profissional",
            render: (_, item) => item.profissional_nome || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "especialidade_nome",
            label: "Especialidade",
            render: (_, item) => item.especialidade_nome || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "qtd_sess",
            label: "Qtd Sess",
            render: (_, item) => item.schedule_qtd_sessions?.toString() || "1",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "status",
            label: "Status Agdmto.",
            render: (_, item) => {
                const statusMap: Record<string, { label: string, color: string }> = {
                    "agendado": { label: "Agendado", color: "bg-blue-100 text-blue-800" },
                    "confirmado": { label: "Confirmado", color: "bg-green-100 text-green-800" },
                    "cancelado": { label: "Cancelado", color: "bg-red-100 text-red-800" },
                    "realizado": { label: "Realizado", color: "bg-purple-100 text-purple-800" },
                    "faltou": { label: "Faltou", color: "bg-orange-100 text-orange-800" }
                };
                const status = statusMap[item.status?.toLowerCase()] || { 
                    label: item.status || 'N/D', 
                    color: "bg-gray-100 text-gray-800" 
                };
                return (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                        {status.label}
                    </span>
                );
            },
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "status_vinculacao",
            label: "Status Vínculo",
            render: (_, item) => {
                const status = item.status_vinculacao || 'Pendente';
                let colorClass = "bg-gray-100 text-gray-800"; // Default: Pendente
                if (status === 'Completo') {
                    colorClass = "bg-green-100 text-green-800";
                } else if (status === 'Ficha OK') {
                    colorClass = "bg-blue-100 text-blue-800";
                } else if (status === 'Unimed OK') {
                    colorClass = "bg-purple-100 text-purple-800";
                } else if (status === 'Pendente') {
                    colorClass = "bg-yellow-100 text-yellow-800";
                }
                // Adicionar outros status como 'Divergência' se necessário

                return (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}>
                        {status}
                    </span>
                );
            },
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "possui_sessao_vinculada",
            label: "Vínculo Ficha",
            render: (_, item) => {
                const vinculado = item.possui_sessao_vinculada;
                return (
                    <span title={vinculado ? "Ficha Vinculada" : "Ficha Não Vinculada"}>
                        {vinculado ? 
                            <CheckCircle2 className="h-5 w-5 text-green-500" /> : 
                            <XCircle className="h-5 w-5 text-red-500" />
                        }
                    </span>
                );
            },
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "possui_execucao_vinculada",
            label: "Vínculo Unimed",
            render: (_, item) => {
                const vinculado = item.possui_execucao_vinculada;
                return (
                    <span title={vinculado ? "Unimed Vinculada" : "Unimed Não Vinculada"}>
                        {vinculado ? 
                            <CheckCircle2 className="h-5 w-5 text-green-500" /> : 
                            <XCircle className="h-5 w-5 text-red-500" />
                        }
                    </span>
                 );
            },
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "schedule_elegibilidade",
            label: "Elegibilidade",
            render: (_, item) => {
                if (item.schedule_elegibilidade === true) return "Sim";
                if (item.schedule_elegibilidade === false) return "Não";
                return "-";
            },
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "schedule_parent_id",
            label: "Id Pai (ABA)",
            render: (_, item) => item.schedule_parent_id || "-",
            visibleByDefault: true,
            sortable: true
        },
        {
            key: "schedule_codigo_faturamento",
            label: "Código Faturamento (ABA)",
            render: (_, item) => item.schedule_codigo_faturamento || "-",
            visibleByDefault: true,
            sortable: true
        },

        // Colunas Não Visíveis por Padrão (restantes ou com origem incerta)
        {
            key: "hora_fim",
            label: "Hora final",
            render: (_, item) => item.hora_fim,
            visibleByDefault: false,
            sortable: true
        },
        {
            key: "procedimento_nome",
            label: "Procedimento (Nome)",
            render: (_, item) => item.procedimento_nome || "-",
            visibleByDefault: false,
            sortable: true
        },
        {
            key: "profissao",
            label: "Profissão",
            render: (_, item) => item.profissao || "-",
            visibleByDefault: false,
            sortable: true
        },
        {
            key: "observacoes",
            label: "Observações",
            render: (_, item) => {
                if (!item.observacoes) return "-";
                const maxLength = 50;
                const text = item.observacoes;
                if (text.length <= maxLength) return text;
                return (
                    <span title={text}>
                        {text.substring(0, maxLength)}...
                    </span>
                );
            },
            visibleByDefault: false,
            sortable: true
        },
        {
            key: "pagamento",
            label: "Pagamento (Antigo)",
            render: (_, item) => item.pagamento || "N/A",
            visibleByDefault: false, 
            sortable: true
        },
        {
            key: "substituicao",
            label: "Substituição",
            render: (_, item) => {
                if (item.schedule_falha_do_profissional === false) return "Sim"; 
                if (item.schedule_falha_do_profissional === true) return "Não";
                return "-"; 
            },
            visibleByDefault: false, 
            sortable: true
        },
        {
            key: "tipo_falta",
            label: "Tipo de Falta",
            render: (_, item) => item.tipo_falta || (item.status?.toLowerCase() === "faltou" ? "N" : "-"),
            visibleByDefault: false, 
            sortable: true 
        },
        {
            key: "acoes",
            label: "Ações",
            render: (_, item) => (
                <div className="flex space-x-2">
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-8 px-2 text-blue-600"
                        onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(item);
                        }}
                    >
                        Editar
                    </Button>
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-8 px-2 text-red-600"
                        onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(item.id);
                        }}
                    >
                        Excluir
                    </Button>
                </div>
            ),
            visibleByDefault: true,
            sortable: false
        }
    ];

    return (
        <div className="p-8">
            <div className="mb-8">
                <h1 className="text-2xl font-semibold text-slate-900">Agendamentos</h1>
                <p className="text-slate-500">Gerencie os agendamentos de pacientes</p>
            </div>

            <div className="flex flex-col sm:flex-row justify-between gap-3 mb-4">
                <Input
                    placeholder="Buscar agendamentos..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="sm:max-w-xs"
                />
                <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-gray-500" />
                    <Select 
                        value={statusVinculacaoFilter} 
                        onValueChange={setStatusVinculacaoFilter}
                    >
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Status Vínculo" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todos Status</SelectItem>
                            <SelectItem value="Pendente">Pendente</SelectItem>
                            <SelectItem value="Ficha OK">Ficha OK</SelectItem>
                            <SelectItem value="Unimed OK">Unimed OK</SelectItem>
                            <SelectItem value="Completo">Completo</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="flex flex-wrap gap-2 justify-end flex-grow">
                    <Button
                        onClick={handleVincularAgendamentos}
                        variant="outline"
                        className="gap-2 flex-nowrap"
                        size="sm"
                        disabled={isLinking}
                    >
                        {isLinking ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                            <Link2 className="h-4 w-4" />
                        )}
                        <span>{isLinking ? "Vinculando..." : "Vincular Agdmts."}</span>
                    </Button>
                    <Button
                        onClick={handleCorrigirMapeamentos}
                        variant="outline"
                        className="gap-2 flex-nowrap"
                        size="sm"
                    >
                        <RefreshCcw className="h-4 w-4" />
                        <span>Corrigir Mapeamentos</span>
                    </Button>
                    <Button
                        onClick={() => setIsImportModalOpen(true)}
                        variant="outline"
                        className="gap-2 flex-nowrap"
                        size="sm"
                    >
                        <Database className="h-4 w-4" />
                        <span>Importar</span>
                    </Button>
                    <Button
                        onClick={handleExportToExcel}
                        variant="outline"
                        className="gap-2 flex-nowrap"
                        size="sm"
                    >
                        <FileDown className="h-4 w-4" />
                        <span>Exportar</span>
                    </Button>
                    <Link href="/agendamento/grafico">
                        <Button 
                            variant="outline"
                            size="sm"
                        >
                            Ver Gráfico
                        </Button>
                    </Link>
                    <Button
                        onClick={() => {
                            setSelectedAgendamento(undefined);
                            setIsModalOpen(true);
                        }}
                        variant="outline"
                        size="sm"
                        className="gap-2 flex-nowrap"
                    >
                        <Plus className="h-4 w-4" />
                        <span>Novo Agendamento</span>
                    </Button>
                </div>
            </div>

            <SortableTableWithColumnSelector
                data={data?.items || []}
                columns={columns}
                loading={isLoading}
                pageCount={data?.total_pages || 1}
                pageIndex={page - 1}
                pageSize={limit}
                totalRecords={data?.total || 0}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
                sortable={true}
                onSort={(column: string, direction: "asc" | "desc") => {
                    setOrderColumn(column);
                    setOrderDirection(direction);
                }}
                initialSortColumn={orderColumn}
                initialSortDirection={orderDirection}
            />

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Confirmar exclusão</DialogTitle>
                        <DialogDescription>
                            Tem certeza que deseja excluir este agendamento? Esta ação não pode ser desfeita.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="gap-2">
                        <Button
                            variant="outline"
                            onClick={() => setIsDeleteDialogOpen(false)}
                        >
                            Cancelar
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={confirmDelete}
                        >
                            Excluir
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <Dialog open={isImportModalOpen} onOpenChange={setIsImportModalOpen}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle>Importar Agendamentos</DialogTitle>
                        <DialogDescription className="pt-2">
                            Importar agendamentos a partir de uma data específica do sistema legado para o sistema atual.
                        </DialogDescription>
                    </DialogHeader>
                    
                    <div className="grid gap-6 py-4">
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="dataInicial" className="font-medium">
                                Data Inicial
                            </Label>
                            <Input
                                id="dataInicial"
                                type="date"
                                value={dataInicial}
                                onChange={(e) => setDataInicial(e.target.value)}
                                className="w-full"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                Importar agendamentos a partir desta data
                            </p>
                        </div>
                        
                        <div className="flex flex-col gap-2">
                            <Label htmlFor="dataFinal" className="font-medium">
                                Data Final
                            </Label>
                            <Input
                                id="dataFinal"
                                type="date"
                                value={dataFinal}
                                onChange={(e) => setDataFinal(e.target.value)}
                                className="w-full"
                            />
                            <p className="text-xs text-muted-foreground mt-1">
                                Importar agendamentos até esta data
                            </p>
                        </div>
                    </div>
                    
                    {recordCount !== null && !showImportConfirmation && !isImporting && (
                        <div className="p-4 rounded-md bg-blue-50 my-4">
                            <p className="text-sm">
                                {recordCount === 0 
                                    ? "Não há registros para importar nesta data." 
                                    : `Existem ${recordCount} registros para importar.`}
                            </p>
                        </div>
                    )}
                    
                    {showImportConfirmation && (
                        <div className="p-5 rounded-md bg-amber-50 border border-amber-200 my-4">
                            <div className="flex items-start gap-3">
                                <AlertTriangle className="h-6 w-6 text-amber-500 mt-0.5 flex-shrink-0" />
                                <div>
                                    <h4 className="text-sm font-medium mb-2">Atenção - Grande volume de dados</h4>
                                    <p className="mt-2 text-sm">
                                        A importação inclui <strong>{recordCount}</strong> registros. 
                                        Este processo pode demorar vários minutos.
                                    </p>
                                    <p className="mt-3 text-sm">
                                        Período de importação: de <strong>{formatarData(dataInicial)}</strong> até <strong>{formatarData(dataFinal)}</strong>
                                    </p>
                                    <p className="mt-3 text-sm">
                                        Deseja continuar com a importação?
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    {isImporting && (
                        <div className="p-4 rounded-md bg-blue-50 my-4">
                            <h4 className="text-sm font-medium mb-2">Importação em andamento</h4>
                            <p className="text-sm mb-2">{importStatus}</p>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                                <div 
                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-in-out" 
                                    style={{ width: `${importProgress}%` }}
                                ></div>
                            </div>
                            <p className="text-xs text-right mt-1">{importProgress}%</p>
                        </div>
                    )}
                    
                    {importResult && (
                        <div className={`p-4 rounded-md ${importResult.success ? 'bg-green-50' : 'bg-red-50'} my-4`}>
                            <h4 className="text-sm font-medium mb-2">Resultado da Importação</h4>
                            <p className="mt-2 text-sm">{importResult.message}</p>
                            
                            {importResult.success && (
                                <div className="mt-3 text-xs space-y-2">
                                    <p>Importados: {importResult.importados} de {importResult.total}</p>
                                    {importResult.total_atualizados !== undefined && (
                                        <p>Atualizados: {importResult.total_atualizados}</p>
                                    )}
                                    {importResult.total_erros !== undefined && importResult.total_erros > 0 && (
                                        <p>Erros: {importResult.total_erros}</p>
                                    )}
                                    {importResult.data_inicial && (
                                        <p>Data inicial: {formatarData(importResult.data_inicial)}</p>
                                    )}
                                </div>
                            )}
                            
                            {importResult.erros && importResult.erros.length > 0 && (
                                <div className="mt-3">
                                    <h5 className="text-xs font-medium mb-1">Erros encontrados:</h5>
                                    <ul className="text-xs mt-2 list-disc list-inside space-y-1">
                                        {importResult.erros.map((erro, index) => (
                                            <li key={index}>
                                                {typeof erro === 'string' 
                                                    ? erro 
                                                    : `Agendamento ${erro.agendamento}: ${erro.erro}`}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                    
                    <DialogFooter className="gap-3 pt-4">
                        {showImportConfirmation && (
                            <>
                                <Button
                                    onClick={() => {
                                        setShowImportConfirmation(false);
                                        setIsImportModalOpen(false);
                                        setRecordCount(null);
                                        setImportResult(null);
                                    }}
                                    variant="outline"
                                >
                                    Cancelar
                                </Button>
                                <Button
                                    onClick={handleImportAgendamentos}
                                    variant="default"
                                >
                                    Continuar importação
                                </Button>
                            </>
                        )}
                        
                        {!isImporting && !showImportConfirmation && !importResult && (
                            <Button
                                onClick={checkRecordCount}
                                disabled={isCheckingCount}
                                variant="outline"
                                className="gap-2"
                            >
                                {isCheckingCount ? (
                                    <>
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        Verificando...
                                    </>
                                ) : (
                                    <>
                                        <Database className="h-4 w-4" />
                                        Verificar e Importar
                                    </>
                                )}
                            </Button>
                        )}
                        
                        {importResult && (
                            <Button
                                onClick={() => {
                                    setIsImportModalOpen(false);
                                    setRecordCount(null);
                                    setShowImportConfirmation(false);
                                    setImportResult(null);
                                    setImportStatus("");
                                    setImportProgress(0);
                                    setIsImporting(false);
                                }}
                                variant="default"
                            >
                                Fechar
                            </Button>
                        )}
                        
                        {!showImportConfirmation && !importResult && (
                            <Button
                                variant="ghost"
                                onClick={() => {
                                    setIsImportModalOpen(false);
                                    setRecordCount(null);
                                    setShowImportConfirmation(false);
                                    setImportResult(null);
                                    setImportStatus("");
                                    setImportProgress(0);
                                    setIsImporting(false);
                                }}
                            >
                                Cancelar
                            </Button>
                        )}
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Adicionar o modal de agendamento quando for criado */}
            {/* <AgendamentoModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedAgendamento(undefined);
                }}
                agendamento={selectedAgendamento}
            /> */}
        </div>
    );
}