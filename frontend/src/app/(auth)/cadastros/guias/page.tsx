"use client"

import { useState, useEffect } from "react"
import { Guia } from "@/types/guia"
import { useGuias } from "@/hooks/useGuias"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Plus, ChevronLeft, FileDown } from "lucide-react"
import { GuiaModal } from "@/components/guias/GuiaModal"
import { SortableTable } from "@/components/ui/SortableTable"
import { columns } from "@/components/guias/columns"
import { TableActions } from "@/components/ui/table-actions"
import { useDebounce } from "@/hooks/useDebounce"
import { guiaService } from "@/services/guiaService"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import Link from "next/link"
import * as XLSX from 'xlsx'

export default function GuiasPage() {
    const [page, setPage] = useState(1)
    const [limit, setLimit] = useState(10)
    const [search, setSearch] = useState("")
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [selectedGuia, setSelectedGuia] = useState<Guia | undefined>()
    const [orderColumn, setOrderColumn] = useState("numero_guia")
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("asc")
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
    const [guiaToDelete, setGuiaToDelete] = useState<string | null>(null)

    const debouncedSearch = useDebounce(search, 500)

    const { data, isLoading, refetch } = useGuias(
        page,
        limit,
        debouncedSearch ? { search: debouncedSearch } : undefined,
        orderColumn,
        orderDirection
    )

    // useEffect(() => {
    //     if (data?.items) {
    //         // console.group('Dados das guias')
    //         // console.log('Total de guias:', data.items.length)
    //         // console.log('Exemplo de guia:', data.items[0])
    //         // console.log('Campos da primeira guia:', Object.keys(data.items[0] || {}))
    //         // console.groupEnd()
    //     }
    // }, [data])

    useEffect(() => {
        if (!isModalOpen) {
            setSelectedGuia(undefined);
        }
    }, [isModalOpen]);

    const handleEdit = (guia: Guia) => {
        setSelectedGuia(guia)
        setIsModalOpen(true)
    }

    const handleDelete = async (id: string) => {
        setGuiaToDelete(id)
        setIsDeleteDialogOpen(true)
    }

    const confirmDelete = async () => {
        if (!guiaToDelete) return

        try {
            await guiaService.excluir(guiaToDelete)
            toast.success("Guia excluída com sucesso!")
            refetch()
        } catch (err) {
            console.error('Erro ao excluir guia:', err)
            toast.error("Erro ao excluir guia")
        } finally {
            setIsDeleteDialogOpen(false)
            setGuiaToDelete(null)
        }
    }

    const formatDateTime = (date: string | undefined) => {
        if (!date) return '-'
        return new Date(date).toLocaleString()
    }

    const handleExportToExcel = () => {
        try {
            const exportData = data?.items.map(guia => ({
                'Número da Guia': guia.numero_guia,
                'ID da Carteirinha': guia.carteirinha_id,
                'ID do Paciente': guia.paciente_id,
                'ID do Procedimento': guia.procedimento_id,
                'Data de Solicitação': formatDateTime(guia.data_solicitacao),
                'Tipo': guia.tipo,
                'Status': guia.status,
                'Quantidade Solicitada': guia.quantidade_solicitada,
                'Quantidade Autorizada': guia.quantidade_autorizada,
                'Quantidade Executada': guia.quantidade_executada,
                'Motivo da Negação': guia.motivo_negacao || '-',
                'Código do Serviço': guia.codigo_servico || '-',
                'Descrição do Serviço': guia.descricao_servico || '-',
                'Observações': guia.observacoes || '-',
                'Data de Autorização': guia.dados_autorizacao?.data_autorizacao || '-',
                'Código de Autorização': guia.dados_autorizacao?.codigo_autorizacao || '-',
                'Autorizador': guia.dados_autorizacao?.autorizador || '-',
                'Data de Criação': formatDateTime(guia.created_at),
                'Última Atualização': formatDateTime(guia.updated_at),
                'Criado por': guia.created_by || '-',
                'Atualizado por': guia.updated_by || '-'
            }));

            if (!exportData) return;

            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Guias');
            XLSX.writeFile(wb, 'guias.xlsx');

            toast.success('Arquivo exportado com sucesso!');
        } catch (error) {
            console.error('Erro ao exportar arquivo:', error);
            toast.error('Erro ao exportar arquivo');
        }
    };

    // Removendo a coluna actions do columns importado
    const columnsWithoutActions = columns.filter(col => col.key !== 'actions');

    const allColumns = [
        ...columnsWithoutActions,
        {
            key: "actions",
            label: "Ações",
            render: (_: unknown, item: Guia) => (
                <TableActions
                    onEdit={() => handleEdit(item)}
                    onDelete={() => handleDelete(item.id)}
                />
            ),
        },
    ]

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Guias</h1>
                    <Link
                        href="/cadastros"
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie o cadastro de guias</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar guias..."
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
                        Nova Guia
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
                        setOrderColumn(column)
                        setOrderDirection(direction)
                    }}
                />
            </div>

            <GuiaModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                onSuccess={refetch}
                initialData={selectedGuia}
            />

            <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>Confirmar exclusão</DialogTitle>
                        <DialogDescription>
                            Tem certeza que deseja excluir esta guia? Esta ação não pode ser desfeita.
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
        </div>
    )
} 