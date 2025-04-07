"use client";

import { useState } from "react";
import { Paciente } from "@/types/paciente";
import { usePacientes, useUltimaAtualizacaoPacientes } from "@/hooks/usePacientes";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown, Database, Loader2 } from "lucide-react";
import { PacienteModal } from "@/components/pacientes/PacienteModal";
import { SortableTable } from "@/components/ui/SortableTable";
import { columns } from "@/components/pacientes/columns";
import { TableActions } from "@/components/ui/table-actions";
import { useDebounce } from "@/hooks/useDebounce";
import { pacienteService } from "@/services/pacienteService";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import Link from "next/link";
import * as XLSX from 'xlsx';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// Valores fixos para a importação
const BANCO_DADOS_PADRAO = "abalarissa_db";
const TABELA_PADRAO = "ps_clients";

export default function PacientesPage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedPaciente, setSelectedPaciente] = useState<Paciente | undefined>();
    const [orderColumn, setOrderColumn] = useState("nome");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("asc");
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [pacienteToDelete, setPacienteToDelete] = useState<string | null>(null);
    
    // Estado para o modal de importação
    const [isImportModalOpen, setIsImportModalOpen] = useState(false);
    const [importLimit, setImportLimit] = useState<number | undefined>(undefined);
    const [isImporting, setIsImporting] = useState(false);
    const [importResult, setImportResult] = useState<{
        message: string;
        importados: number;
        total: number;
        total_atualizados?: number;
        total_erros?: number;
        erros: Array<string | { paciente: string, erro: string }>;
        success: boolean;
        connection_status: {
            success: boolean;
            message: string;
        };
    } | null>(null);

    const debouncedSearch = useDebounce(search, 500);

    const { data, isLoading, refetch } = usePacientes(
        page,
        limit,
        debouncedSearch,
        orderColumn,
        orderDirection
    );

    // const { data: ultimaAtualizacao } = useUltimaAtualizacaoPacientes();

    const handleEdit = (paciente: Paciente) => {
        setSelectedPaciente(paciente);
        setIsModalOpen(true);
    };

    const handleDelete = async (id: string) => {
        setPacienteToDelete(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!pacienteToDelete) return;

        try {
            await pacienteService.excluir(pacienteToDelete);
            toast.success("Paciente excluído com sucesso!");
            refetch();
        } catch (error) {
            toast.error("Erro ao excluir paciente");
        } finally {
            setIsDeleteDialogOpen(false);
            setPacienteToDelete(null);
        }
    };

    const formatDateTime = (date: string | undefined) => {
        if (!date) return "";
        return new Date(date).toLocaleString("pt-BR");
    };

    const handleExportToExcel = () => {
        try {
            const exportData = data?.items.map(paciente => ({
                Nome: paciente.nome,
                'Nome do Responsável': paciente.nome_responsavel,
                'Nome do Pai': paciente.nome_pai,
                'Nome da Mãe': paciente.nome_mae,
                'Data de Nascimento': paciente.data_nascimento,
                CPF: paciente.cpf,
                'CPF do Responsável': paciente.cpf_responsavel,
                RG: paciente.rg,
                Sexo: paciente.sexo,
                Telefone: paciente.telefone,
                Email: paciente.email,
                CEP: paciente.cep,
                Endereço: paciente.endereco,
                Número: paciente.numero,
                Complemento: paciente.complemento,
                Bairro: paciente.bairro,
                Cidade: paciente.cidade,
                Estado: paciente.estado,
                'Forma de Pagamento': paciente.forma_pagamento,
                'Valor da Consulta': paciente.valor_consulta,
                'Nome da Escola': paciente.escola_nome,
                'Ano Escolar': paciente.escola_ano,
                'Professor': paciente.escola_professor,
                'Período Escolar': paciente.escola_periodo,
                'Contato da Escola': paciente.escola_contato,
                'Tem Supervisor': paciente.tem_supervisor ? 'Sim' : 'Não',
                'Tem Avaliação Luria': paciente.tem_avaliacao_luria ? 'Sim' : 'Não',
                'Data Início Treinamento Luria': paciente.avaliacao_luria_data_inicio_treinamento,
                'Reforçadores Luria': paciente.avaliacao_luria_reforcadores,
                'Observações Comportamento Luria': paciente.avaliacao_luria_obs_comportamento,
                'Número Carteirinha': paciente.numero_carteirinha,
                'CRM Médico': paciente.crm_medico,
                'Nome do Médico': paciente.nome_medico,
                'Pai Não Declarado': paciente.pai_nao_declarado ? 'Sim' : 'Não',
                'Observações': paciente.observacoes,
                'Data de Criação': formatDateTime(paciente.created_at),
                'Última Atualização': formatDateTime(paciente.updated_at)
            }));

            if (!exportData) return;

            // Criar planilha
            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Pacientes");

            // Ajustar largura das colunas
            const wscols = Object.keys(exportData[0]).map(() => ({ wch: 20 })); // width 20 para todas as colunas
            ws['!cols'] = wscols;

            // Gerar arquivo e fazer download
            XLSX.writeFile(wb, "pacientes.xlsx");
            
            toast.success("Dados exportados com sucesso!");
        } catch (err) {
            console.error("Erro ao exportar dados:", err);
            toast.error("Erro ao exportar dados");
        }
    };
    
    const handleImportPacientes = async () => {
        setIsImporting(true);
        setImportResult(null);
        
        try {
            const result = await pacienteService.importarPacientes(
                BANCO_DADOS_PADRAO,
                TABELA_PADRAO,
                importLimit
            );
            
            setImportResult(result);
            
            // Usar mensagem segura para o toast
            if (result.success) {
                const mensagem = result.total_atualizados && result.total_atualizados > 0
                    ? `Importação concluída: ${result.importados - (result.total_atualizados || 0)} novos e ${result.total_atualizados} atualizados`
                    : `Importação concluída: ${result.importados} de ${result.total} pacientes importados`;
                
                toast.success(mensagem);
            } else {
                toast.error(`Falha na importação: ${result.message}`);
            }
            
            // Atualizar a lista após importação bem-sucedida
            refetch();
        } catch (error) {
            console.error("Erro na importação:", error);
            toast.error("Erro ao importar pacientes");
        } finally {
            setIsImporting(false);
        }
    };

    const allColumns = [
        ...columns,
        {
            key: "actions",
            label: "Ações",
            render: (_: unknown, paciente: Paciente) => (
                <TableActions
                    onEdit={() => handleEdit(paciente)}
                    onDelete={() => handleDelete(paciente.id)}
                />
            ),
        },
    ];

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Pacientes</h1>
                    <Link 
                        href="/cadastros" 
                        className="ml-auto flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie o cadastro de pacientes</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar pacientes..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="max-w-sm"
                />
                <div className="flex gap-2">
                    <Button
                        onClick={() => setIsImportModalOpen(true)}
                        variant="outline"
                        className="bg-white hover:bg-gray-50"
                    >
                        <Database className="mr-2 h-4 w-4" />
                        Importar
                    </Button>
                    <Button
                        onClick={handleExportToExcel}
                        variant="outline"
                        className="bg-white hover:bg-gray-50"
                    >
                        <FileDown className="mr-2 h-4 w-4" />
                        Exportar Excel
                    </Button>
                    <Button
                        onClick={() => {
                            setSelectedPaciente(undefined);
                            setIsModalOpen(true);
                        }}
                        variant="outline"
                        className="bg-white hover:bg-gray-50"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        Novo Paciente
                    </Button>
                </div>
            </div>

            <div className="bg-white rounded-lg border shadow-sm">
                <SortableTable
                    data={data?.items || []}
                    columns={allColumns}
                    loading={isLoading}
                    pageCount={data?.total_pages || 1}
                    pageIndex={page - 1}
                    pageSize={limit}
                    totalRecords={data?.total || 0}
                    onPageChange={(newPage) => setPage(newPage + 1)}
                    onPageSizeChange={(newSize) => {
                        setLimit(newSize);
                        setPage(1);
                    }}
                    sortable
                    onSort={(column, direction) => {
                        setOrderColumn(column);
                        setOrderDirection(direction);
                    }}
                    // lastUpdateDate={ultimaAtualizacao?.data?.ultima_atualizacao}
                />
            </div>

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Confirmar exclusão</DialogTitle>
                        <DialogDescription>
                            Tem certeza que deseja excluir este paciente? Esta ação não pode ser desfeita.
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
            
            {/* Modal de Importação Simplificado */}
            <Dialog 
                open={isImportModalOpen} 
                onOpenChange={(open) => {
                    // Só permite fechar a modal através do botão Cancelar
                    if (open === false && isImportModalOpen === true) {
                        return;
                    }
                    setIsImportModalOpen(open);
                }}
            >
                <DialogContent 
                    className="sm:max-w-[500px]"
                    onEscapeKeyDown={(e) => {
                        // Previne o fechamento ao pressionar ESC
                        e.preventDefault();
                    }}
                    onInteractOutside={(e) => {
                        // Previne o fechamento ao clicar fora
                        e.preventDefault();
                    }}
                >
                    <DialogHeader>
                        <DialogTitle>Importar Pacientes</DialogTitle>
                        <DialogDescription>
                            Importe pacientes do banco MySQL para o Supabase.
                        </DialogDescription>
                    </DialogHeader>
                    
                    <div className="space-y-4">
                        {/* Informações sobre a importação */}
                        <div className="bg-muted p-3 rounded-md text-sm">
                            <p>Serão importados pacientes da tabela <strong>{TABELA_PADRAO}</strong> do banco de dados <strong>{BANCO_DADOS_PADRAO}</strong>.</p>
                            <p className="mt-2">Os dados serão mapeados automaticamente para os campos correspondentes na tabela de pacientes.</p>
                        </div>
                        
                        <div className="space-y-2">
                            <label htmlFor="limit" className="text-sm font-medium">
                                Limite de Registros (opcional)
                            </label>
                            <Input
                                id="limit"
                                type="number"
                                placeholder="Deixe em branco para importar todos"
                                value={importLimit || ""}
                                onChange={(e) => {
                                    const value = e.target.value;
                                    setImportLimit(value ? parseInt(value) : undefined);
                                }}
                                // disabled={isImporting}
                                disabled
                            />
                        </div>
                        
                        {importResult && (
                            <div className={`p-3 rounded-md text-sm ${importResult.success ? 'bg-green-50' : 'bg-red-50'}`}>
                                {/* Status da conexão */}
                                <div className="mb-2">
                                    <p className="font-medium">Status da conexão:</p>
                                    {importResult.connection_status.success ? (
                                        <p className="text-green-600">✓ Conectado ao banco de dados com sucesso</p>
                                    ) : (
                                        <p className="text-red-600">✗ Falha na conexão com o banco de dados</p>
                                    )}
                                    <p className="text-xs mt-1">{importResult.connection_status.message}</p>
                                </div>
                                
                                {/* Resultado da importação */}
                                <p className="font-medium">{importResult.message}</p>
                                <p>Importados: {importResult.importados} de {importResult.total}</p>
                                {importResult && importResult.erros && importResult.erros.length > 0 && (
                                    <div className="mt-4">
                                        <h4 className="font-semibold text-md">Erros ({importResult.erros.length}):</h4>
                                        <ul className="list-disc pl-5 mt-2 space-y-1 max-h-60 overflow-y-auto">
                                            {importResult.erros.map((erro, index) => (
                                                <li key={index} className="text-destructive">
                                                    {typeof erro === 'string' 
                                                        ? erro 
                                                        : `${erro.paciente}: ${erro.erro}`}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                    
                    <DialogFooter className="gap-2">
                        <Button
                            variant="outline"
                            onClick={() => setIsImportModalOpen(false)}
                            disabled={isImporting}
                        >
                            Cancelar
                        </Button>
                        <Button
                            onClick={handleImportPacientes}
                            disabled={isImporting}
                        >
                            {isImporting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Importando...
                                </>
                            ) : (
                                "Importar Pacientes"
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <PacienteModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedPaciente(undefined);
                }}
                paciente={selectedPaciente}
            />
        </div>
    );
}