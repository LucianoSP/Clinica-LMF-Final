"use client";

import { useState, useEffect } from "react";
import { Execucao } from "@/types/execucao";
import { useExecucoes } from "@/hooks/useExecucoes";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown } from "lucide-react";
import { ExecucaoModal } from "@/components/execucoes/ExecucaoModal";
import { SortableTable } from "@/components/ui/SortableTable";
import { columns } from "@/components/execucoes/columns";
import { TableActions } from "@/components/ui/table-actions";
import { useDebounce } from "@/hooks/useDebounce";
import { execucaoService } from "@/services/execucaoService";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import Link from "next/link";
import * as XLSX from 'xlsx';
import { formatarData } from "@/lib/utils";

export default function ExecucoesPage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedExecucao, setSelectedExecucao] = useState<Execucao | undefined>();
    const [orderColumn, setOrderColumn] = useState("data_execucao");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("desc");
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [execucaoToDelete, setExecucaoToDelete] = useState<string | null>(null);

    const debouncedSearch = useDebounce(search, 500);

    const { data, isLoading, refetch } = useExecucoes(
        page,
        limit,
        debouncedSearch,
        orderColumn,
        orderDirection
    );

    // Depuração para verificar os dados recebidos
    useEffect(() => {
        if (data) {
            console.log("Dados completos recebidos:", data);
            
            // Verificar se há items na resposta
            if (!data.items || data.items.length === 0) {
                console.warn("Não há items na resposta da API");
                return;
            }
            
            // Verificar o primeiro item
            const primeiroItem = data.items[0];
            console.log("Primeiro item (após processamento):", primeiroItem);
            
            // Verificar se os campos necessários estão presentes
            const camposEsperados = [
                'paciente_nome', 'paciente_carteirinha', 'numero_guia', 
                'codigo_ficha', 'status_biometria', 'origem', 'profissional_executante'
            ];
            
            const camposPresentes = camposEsperados.filter(campo => primeiroItem[campo as keyof typeof primeiroItem]);
            const camposAusentes = camposEsperados.filter(campo => !primeiroItem[campo as keyof typeof primeiroItem]);
            
            console.log("Campos presentes:", camposPresentes);
            console.log("Campos ausentes:", camposAusentes);
            
            // Verificar campos do banco de dados
            const camposBanco = [
                'id', 'guia_id', 'sessao_id', 'data_execucao', 'data_atendimento',
                'paciente_nome', 'paciente_carteirinha', 'numero_guia', 'codigo_ficha',
                'codigo_ficha_temp', 'usuario_executante', 'origem', 'ip_origem',
                'ordem_execucao', 'status_biometria', 'conselho_profissional',
                'numero_conselho', 'uf_conselho', 'codigo_cbo', 'profissional_executante'
            ];
            
            console.log("Campos do banco presentes:", camposBanco.filter(campo => primeiroItem[campo as keyof typeof primeiroItem]));
            console.log("Campos do banco ausentes:", camposBanco.filter(campo => !primeiroItem[campo as keyof typeof primeiroItem]));
            
            // Verificar as colunas
            console.log("Colunas utilizadas:", columns);
        }
    }, [data]);

    const handleEdit = (execucao: Execucao) => {
        setSelectedExecucao(execucao);
        setIsModalOpen(true);
    };

    const handleDelete = async (id: string) => {
        setExecucaoToDelete(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!execucaoToDelete) return;

        try {
            await execucaoService.excluir(execucaoToDelete);
            toast.success("Execução excluída com sucesso!");
            refetch();
        } catch (err) {
            console.error('Erro ao excluir execução:', err);
            toast.error("Erro ao excluir execução");
        } finally {
            setIsDeleteDialogOpen(false);
            setExecucaoToDelete(null);
        }
    };

    const handleExportToExcel = () => {
        try {
            if (!data || !data.items) {
                toast.error("Não há dados para exportar");
                return;
            }

            const exportData = data.items.map((execucao: Execucao) => ({
                'Data de Execução': formatarData(execucao.data_execucao, true),
                'Data de Atendimento': formatarData(execucao.data_atendimento, true),
                'Paciente': execucao.paciente_nome,
                'Carteirinha': execucao.paciente_carteirinha,
                'Número da Guia': execucao.numero_guia,
                'Código da Ficha': execucao.codigo_ficha,
                'Status Biometria': execucao.status_biometria,
                'Origem': execucao.origem,
                'IP Origem': execucao.ip_origem || '-',
                'Profissional Executante': execucao.profissional_executante || '-',
                'Status': execucao.status,
                'Criado em': formatarData(execucao.created_at, true)
            }));

            if (!exportData || exportData.length === 0) {
                toast.error("Não há dados para exportar");
                return;
            }

            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Execucoes");

            const wscols = Object.keys(exportData[0]).map(() => ({ wch: 20 }));
            ws['!cols'] = wscols;

            XLSX.writeFile(wb, "execucoes.xlsx");
            
            toast.success("Dados exportados com sucesso!");
        } catch (err) {
            console.error("Erro ao exportar dados:", err);
            toast.error("Erro ao exportar dados");
        }
    };

    const allColumns = [
        ...columns,
        {
            key: "actions",
            label: "Ações",
            render: (_: unknown, execucao: Execucao) => (
                <TableActions
                    onEdit={() => handleEdit(execucao)}
                    onDelete={() => handleDelete(execucao.id)}
                />
            ),
        },
    ];

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Execuções</h1>
                    <Link 
                        href="/cadastros" 
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie as execuções de procedimentos</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar execuções..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="max-w-sm"
                />
                <div className="flex gap-2">
                    <Button
                        onClick={handleExportToExcel}
                        variant="outline"
                        className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                    >
                        <FileDown className="mr-2 h-4 w-4" />
                        Exportar Excel
                    </Button>
                    <Button 
                        onClick={() => setIsModalOpen(true)}
                        variant="outline"
                        className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        Nova Execução
                    </Button>
                </div>
            </div>

            <div className="bg-white rounded-lg border shadow-sm">
                <SortableTable
                    data={data?.items || []}
                    columns={allColumns}
                    loading={isLoading}
                    pageCount={data?.total_pages || 0}
                    pageIndex={page - 1}
                    pageSize={limit}
                    totalRecords={data?.total || 0}
                    onPageChange={(newPage) => setPage(newPage + 1)}
                    onPageSizeChange={setLimit}
                    sortable
                    onSort={(column, direction) => {
                        setOrderColumn(column);
                        setOrderDirection(direction);
                    }}
                />
            </div>

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Confirmar exclusão</DialogTitle>
                        <DialogDescription>
                            Tem certeza que deseja excluir esta execução? Esta ação não pode ser desfeita.
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

            <ExecucaoModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedExecucao(undefined);
                }}
                execucao={selectedExecucao}
            />
        </div>
    );
}