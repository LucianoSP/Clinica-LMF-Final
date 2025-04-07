"use client";

import { useState } from "react";
import { Procedimento } from "@/types/procedimento";
import { useProcedimentos } from "@/hooks/useProcedimentos";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown } from "lucide-react";
import { ProcedimentoModal } from "@/components/procedimentos/ProcedimentoModal";
import { SortableTable } from "@/components/ui/SortableTable";
import { columns } from "@/components/procedimentos/columns";
import { TableActions } from "@/components/ui/table-actions";
import { useDebounce } from "@/hooks/useDebounce";
import { procedimentoService } from "@/services/procedimentoService";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import Link from "next/link";
import * as XLSX from 'xlsx';

export default function ProcedimentosPage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedProcedimento, setSelectedProcedimento] = useState<Procedimento | undefined>();
    const [orderColumn, setOrderColumn] = useState("nome");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("asc");
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [procedimentoToDelete, setProcedimentoToDelete] = useState<string | null>(null);

    const debouncedSearch = useDebounce(search, 500);

    const { data, isLoading, refetch } = useProcedimentos(
        page,
        limit,
        debouncedSearch,
        orderColumn,
        orderDirection
    );

    const handleEdit = (procedimento: Procedimento) => {
        setSelectedProcedimento(procedimento);
        setIsModalOpen(true);
    };

    const handleDelete = async (id: string) => {
        setProcedimentoToDelete(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!procedimentoToDelete) return;

        try {
            await procedimentoService.excluir(procedimentoToDelete);
            toast.success("Procedimento excluído com sucesso!");
            refetch();
        } catch (err) {
            console.error('Erro ao excluir procedimento:', err);
            toast.error("Erro ao excluir procedimento");
        } finally {
            setIsDeleteDialogOpen(false);
            setProcedimentoToDelete(null);
        }
    };

    const formatDateTime = (date: string | undefined) => {
        if (!date) return '-';
        return new Date(date).toLocaleString();
    };

    const handleExportToExcel = () => {
        try {
            const exportData = data?.items.map(procedimento => ({
                'Código': procedimento.codigo,
                'Nome': procedimento.nome,
                'Tipo': procedimento.tipo,
                'Valor Base': procedimento.valor,
                'Valor Filme': procedimento.valor_filme,
                'Valor Operacional': procedimento.valor_operacional,
                'Valor Total': procedimento.valor_total,
                'Requer Autorização': procedimento.requer_autorizacao ? 'Sim' : 'Não',
                'Status': procedimento.ativo ? 'Ativo' : 'Inativo',
                'Data de Criação': formatDateTime(procedimento.created_at),
                'Última Atualização': formatDateTime(procedimento.updated_at)
            }));

            if (!exportData) return;

            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Procedimentos");

            const wscols = Object.keys(exportData[0]).map(() => ({ wch: 20 }));
            ws['!cols'] = wscols;

            XLSX.writeFile(wb, "procedimentos.xlsx");
            
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
            render: (_: unknown, procedimento: Procedimento) => (
                <TableActions
                    onEdit={() => handleEdit(procedimento)}
                    onDelete={() => handleDelete(procedimento.id)}
                />
            ),
        },
    ];

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Procedimentos</h1>
                    <Link 
                        href="/cadastros" 
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie o cadastro de procedimentos</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar procedimentos..."
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
                        Novo Procedimento
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
                            Tem certeza que deseja excluir este procedimento? Esta ação não pode ser desfeita.
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

            <ProcedimentoModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedProcedimento(undefined);
                }}
                procedimento={selectedProcedimento}
            />
        </div>
    );
} 