"use client";

import { useState, useRef } from "react";
import { PlanoSaude } from "@/types/plano_saude";
import { usePlanosSaude } from "@/hooks/usePlanosSaude";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown } from "lucide-react";
import { PlanoSaudeModal } from "@/components/planos_saude/PlanoSaudeModal";
import { SortableTable } from "@/components/ui/SortableTable";
import { columns } from "@/components/planos_saude/columns";
import { TableActions } from "@/components/ui/table-actions";
import { useDebounce } from "@/hooks/useDebounce";
import { planoSaudeService } from "@/services/planoSaudeService";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import Link from "next/link";
import * as XLSX from 'xlsx';

export default function PlanosSaudePage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedPlano, setSelectedPlano] = useState<PlanoSaude | undefined>();
    const [orderColumn, setOrderColumn] = useState("nome");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("asc");
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [planoToDelete, setPlanoToDelete] = useState<string | null>(null);

    const debouncedSearch = useDebounce(search, 500);

    const { data, isLoading, refetch } = usePlanosSaude(
        page,
        limit,
        debouncedSearch,
        orderColumn,
        orderDirection
    );

    const handleEdit = (plano: PlanoSaude) => {
        setSelectedPlano(plano);
        setIsModalOpen(true);
    };

    const handleDelete = async (id: string) => {
        setPlanoToDelete(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!planoToDelete) return;

        try {
            await planoSaudeService.excluir(planoToDelete);
            toast.success("Plano de saúde excluído com sucesso!");
            refetch();
        } catch (err) {
            console.error('Erro ao excluir plano de saúde:', err);
            toast.error("Erro ao excluir plano de saúde");
        } finally {
            setIsDeleteDialogOpen(false);
            setPlanoToDelete(null);
        }
    };

    const handleExportToExcel = () => {
        try {
            const exportData = data?.items.map(plano => ({
                'Código da Operadora': plano.codigo_operadora,
                'Registro ANS': plano.registro_ans,
                'Nome do Plano': plano.nome,
                'Tipo do Plano': plano.tipo_plano || '',
                'Abrangência': plano.abrangencia || '',
                'Status': plano.ativo ? 'Ativo' : 'Inativo',
                'Observações': plano.observacoes || '',
                'Data de Criação': plano.created_at ? new Date(plano.created_at).toLocaleDateString('pt-BR') : '',
                'Última Atualização': plano.updated_at ? new Date(plano.updated_at).toLocaleDateString('pt-BR') : '',
            }));

            if (!exportData) return;

            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Planos de Saúde");

            const wscols = Object.keys(exportData[0]).map(() => ({ wch: 20 }));
            ws['!cols'] = wscols;

            XLSX.writeFile(wb, "planos_saude.xlsx");
            
            toast.success("Dados exportados com sucesso!");
        } catch (err) {
            console.error("Erro ao exportar dados:", err);
            toast.error("Erro ao exportar dados");
        }
    };

    const handleSuccess = () => {
        refetch();
        setIsModalOpen(false);
    };

    const allColumns = [
        ...columns,
        {
            key: "actions",
            label: "Ações",
            render: (_: unknown, plano: PlanoSaude) => (
                <TableActions
                    onEdit={() => handleEdit(plano)}
                    onDelete={() => handleDelete(plano.id)}
                />
            ),
        },
    ];

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Planos de Saúde</h1>
                    <Link 
                        href="/cadastros" 
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie o cadastro de planos de saúde</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar planos..."
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
                        Novo Plano
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
                            Tem certeza que deseja excluir este plano de saúde? Esta ação não pode ser desfeita.
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

            <PlanoSaudeModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedPlano(undefined);
                }}
                plano_saude={selectedPlano}
                onSuccess={handleSuccess}
            />
        </div>
    );
}