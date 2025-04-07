"use client";

import { useState } from "react";
import { Carteirinha } from "@/types/carteirinha";
import { useCarteirinhas } from "@/hooks/useCarteirinhas";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown } from "lucide-react";
import { CarteirinhaModal } from "@/components/carteirinhas/CarteirinhaModal";
import { SortableTable } from "@/components/ui/SortableTable";
import { columns } from "@/components/carteirinhas/columns";
import { TableActions } from "@/components/ui/table-actions";
import { useDebounce } from "@/hooks/useDebounce";
import { carteirinhaService } from "@/services/carteirinhaService";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import Link from "next/link";
import * as XLSX from 'xlsx';
import { useQuery } from "@tanstack/react-query";

export default function CarteirinhasPage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedCarteirinha, setSelectedCarteirinha] = useState<Carteirinha | undefined>();
    const [orderColumn, setOrderColumn] = useState("numero_carteirinha");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("asc");
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [carteirinhaToDelete, setCarteirinhaToDelete] = useState<string | null>(null);

    const debouncedSearch = useDebounce(search, 500);

    const { data, isLoading, refetch } = useQuery({
        queryKey: ["carteirinhas", "with-joins", page, limit, debouncedSearch, orderColumn, orderDirection],
        queryFn: () => carteirinhaService.listarComJoins(
            page,
            limit,
            debouncedSearch,
            orderColumn,
            orderDirection,
            undefined,
            undefined,
            undefined
        ),
        staleTime: 1000 * 60, // 1 minuto
    });

    const handleEdit = (carteirinha: Carteirinha) => {
        setSelectedCarteirinha(carteirinha);
        setIsModalOpen(true);
    };

    const handleDelete = async (id: string) => {
        setCarteirinhaToDelete(id);
        setIsDeleteDialogOpen(true);
    };

    const confirmDelete = async () => {
        if (!carteirinhaToDelete) return;

        try {
            await carteirinhaService.excluir(carteirinhaToDelete);
            toast.success("Carteirinha excluída com sucesso!");
            refetch();
        } catch (err) {
            console.error('Erro ao excluir carteirinha:', err);
            toast.error("Erro ao excluir carteirinha");
        } finally {
            setIsDeleteDialogOpen(false);
            setCarteirinhaToDelete(null);
        }
    };

    const formatDateTime = (date: string | undefined) => {
        if (!date) return '-';
        return new Date(date).toLocaleString();
    };

    const handleExportToExcel = () => {
        try {
            const exportData = data?.items.map(carteirinha => ({
                'Número da Carteirinha': carteirinha.numero_carteirinha,
                'ID do Paciente': carteirinha.paciente_id,
                'ID do Plano de Saúde': carteirinha.plano_saude_id,
                'Data de Validade': carteirinha.data_validade,
                'Status': carteirinha.status,
                'Motivo de Inativação': carteirinha.motivo_inativacao || '-',
                'Data de Criação': formatDateTime(carteirinha.created_at),
                'Última Atualização': formatDateTime(carteirinha.updated_at)
            }));

            if (!exportData) return;

            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Carteirinhas");

            const wscols = Object.keys(exportData[0]).map(() => ({ wch: 20 }));
            ws['!cols'] = wscols;

            XLSX.writeFile(wb, "carteirinhas.xlsx");
            
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
            render: (_: unknown, carteirinha: Carteirinha) => (
                <TableActions
                    onEdit={() => handleEdit(carteirinha)}
                    onDelete={() => handleDelete(carteirinha.id)}
                />
            ),
        },
    ];

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Carteirinhas</h1>
                    <Link 
                        href="/cadastros" 
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie o cadastro de carteirinhas</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar carteirinhas..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="max-w-sm"
                />
                <div className="flex gap-2">
                    <Link href="/cadastros/carteirinhas/migrar">
                        <Button
                            variant="outline"
                            className="bg-white hover:bg-blue-50 hover:text-blue-600 hover:border-blue-600 transition-colors"
                        >
                            Migrar Carteirinhas UNIMED
                        </Button>
                    </Link>
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
                        Nova Carteirinha
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
                            Tem certeza que deseja excluir esta carteirinha? Esta ação não pode ser desfeita.
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

            <CarteirinhaModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setSelectedCarteirinha(undefined);
                }}
                carteirinha={selectedCarteirinha}
            />
        </div>
    );
}