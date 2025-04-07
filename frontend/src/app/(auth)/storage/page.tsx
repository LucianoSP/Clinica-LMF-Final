"use client"

import { useState } from "react"
import { Storage } from "@/types/storage"
import { useStorageFiles } from "@/hooks/useStorageFiles"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Plus, ChevronLeft, Download, RefreshCw, Upload } from "lucide-react"
import { StorageModal } from "@/components/storage/StorageModal"
import { SortableTable } from "@/components/ui/SortableTable"
import { columns } from "@/components/storage/columns"
import { useDebounce } from "@/hooks/useDebounce"
import { storageService } from "@/services/storageService"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import Link from "next/link"

export default function StoragePage() {
    const [page, setPage] = useState(1)
    const [limit, setLimit] = useState(10)
    const [search, setSearch] = useState("")
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [selectedStorage, setSelectedStorage] = useState<Storage | undefined>()
    const [orderColumn, setOrderColumn] = useState("nome")
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("desc")
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
    const [storageToDelete, setStorageToDelete] = useState<string | null>(null)
    const [isSyncing, setIsSyncing] = useState(false)
    const [isUploading, setIsUploading] = useState(false)

    const debouncedSearch = useDebounce(search, 500)
    
    const { data, isLoading, refetch } = useStorageFiles({
        page,
        limit,
        search: debouncedSearch,
        order_column: orderColumn,
        order_direction: orderDirection
    })
    
    const handleEdit = (storage: Storage) => {
        setSelectedStorage(storage)
        setIsModalOpen(true)
    }
    
    const handleDelete = async (id: string) => {
        setStorageToDelete(id)
        setIsDeleteDialogOpen(true)
    }
    
    const confirmDelete = async () => {
        if (!storageToDelete) return
        
        try {
            await storageService.excluir(storageToDelete)
            toast.success("Arquivo excluído com sucesso!")
            refetch()
        } catch (err) {
            console.error('Erro ao excluir arquivo:', err)
            toast.error("Erro ao excluir arquivo")
        } finally {
            setIsDeleteDialogOpen(false)
            setStorageToDelete(null)
        }
    }
    
    const handleDownload = (url: string, fileName: string) => {
        try {
            const link = document.createElement('a')
            link.href = url
            link.download = fileName
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
        } catch (err) {
            console.error("Erro ao baixar arquivo:", err)
            toast.error("Erro ao baixar arquivo")
        }
    }

    const handleSync = async () => {
        try {
            setIsSyncing(true);
            await storageService.syncWithR2();
            toast.success("Sincronização bidirecional concluída com sucesso");
            refetch();
        } catch (error) {
            console.error("Erro ao sincronizar:", error);
            toast.error("Erro ao sincronizar com R2");
        } finally {
            setIsSyncing(false);
        }
    };

    const handleUpload = async (files: FileList | null) => {
        if (!files || files.length === 0) return;

        try {
            setIsUploading(true);
            await storageService.uploadFiles(files);
            toast.success("Upload concluído com sucesso");
            refetch();
        } catch (error) {
            console.error("Erro ao fazer upload:", error);
            toast.error("Erro ao fazer upload dos arquivos");
        } finally {
            setIsUploading(false);
        }
    };

    const allColumns = [
        ...columns,
        {
            key: "actions",
            label: "Ações",
            render: (_: unknown, storage: Storage) => (
                <div className="flex gap-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDownload(storage.url, storage.nome)}
                    >
                        <Download className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEdit(storage)}
                    >
                        <Plus className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(storage.id)}
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                </div>
            ),
        },
    ]
    
    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Armazenamento</h1>
                    <Link 
                        href="/cadastros" 
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie os arquivos armazenados no sistema</p>
            </div>

            <div className="flex justify-between items-center gap-4 mb-4">
                <Input
                    placeholder="Buscar arquivos..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="max-w-sm"
                />
                <div className="flex gap-4">
                    <Button
                        onClick={handleSync}
                        disabled={isSyncing}
                        variant="outline"
                        className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                    >
                        <RefreshCw className="mr-2 h-4 w-4" />
                        {isSyncing ? "Sincronizando..." : "Sincronizar R2"}
                    </Button>
                    <Button
                        onClick={() => document.getElementById("fileInput")?.click()}
                        disabled={isUploading}
                        variant="outline"
                        className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                    >
                        <Upload className="mr-2 h-4 w-4" />
                        {isUploading ? "Enviando..." : "Upload"}
                    </Button>
                    <input
                        id="fileInput"
                        type="file"
                        multiple
                        className="hidden"
                        onChange={(e) => handleUpload(e.target.files)}
                    />
                </div>
            </div>

            <div className="bg-white rounded-lg border shadow-sm">
                <SortableTable
                    columns={columns}
                    data={data?.items || []}
                    loading={isLoading}
                    pageCount={Math.ceil((data?.total || 0) / limit)}
                    pageIndex={page - 1}
                    pageSize={limit}
                    totalRecords={data?.total || 0}
                    onPageChange={(newPage) => setPage(newPage + 1)}
                    onPageSizeChange={(newSize) => setLimit(newSize)}
                    sortable={true}
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
                            Tem certeza que deseja excluir este arquivo? Esta ação não pode ser desfeita.
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

            <StorageModal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false)
                    setSelectedStorage(undefined)
                }}
                storage={selectedStorage}
                onSuccess={refetch}
            />
        </div>
    )
}