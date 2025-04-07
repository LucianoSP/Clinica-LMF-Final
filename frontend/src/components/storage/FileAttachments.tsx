"use client"

import { StorageModal } from "./StorageModal"
import { useStorageFilesByReference } from "@/hooks/useStorageFiles"
import { Button } from "../ui/button"
import { FileIcon, Loader2, Download, Plus, Trash } from "lucide-react"
import { useState } from "react"
import { storageService } from "@/services/storageService"
import { toast } from "sonner"
import { formatBytes } from "@/lib/formatters"
import { Storage } from "@/types/storage"

interface FileAttachmentsProps {
    referenceId?: string
    referenceType?: string
    title?: string
    readonly?: boolean
}

export function FileAttachments({ referenceId, referenceType, title = "Anexos", readonly }: FileAttachmentsProps) {
    const [isModalOpen, setIsModalOpen] = useState(false)
    const { files, isLoading, refetch } = useStorageFilesByReference(referenceId, referenceType)

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

    const handleDelete = async (id: string) => {
        try {
            await storageService.excluir(id)
            toast.success("Arquivo removido com sucesso!")
            refetch()
        } catch (err) {
            console.error("Erro ao remover arquivo:", err)
            toast.error("Erro ao remover arquivo")
        }
    }

    if (!referenceId || !referenceType) return null

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">{title}</h3>
                {!readonly && (
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsModalOpen(true)}
                    >
                        <Plus className="h-4 w-4 mr-2" />
                        Adicionar
                    </Button>
                )}
            </div>

            <div className="space-y-2">
                {isLoading ? (
                    <div className="flex items-center justify-center p-4">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                ) : files.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                        Nenhum arquivo anexado
                    </p>
                ) : (
                    <div className="grid gap-2">
                        {files.map((file: Storage) => (
                            <div
                                key={file.id}
                                className="flex items-center justify-between p-2 rounded-lg border bg-muted/20"
                            >
                                <div className="flex items-center gap-2">
                                    <FileIcon className="h-4 w-4 text-muted-foreground" />
                                    <div className="flex flex-col">
                                        <span className="text-sm font-medium">
                                            {file.nome}
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            {formatBytes(file.tamanho)}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => handleDownload(file.url, file.nome)}
                                    >
                                        <Download className="h-4 w-4" />
                                    </Button>
                                    {!readonly && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDelete(file.id)}
                                        >
                                            <Trash className="h-4 w-4 text-destructive" />
                                        </Button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <StorageModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                referenceId={referenceId}
                referenceType={referenceType}
                onSuccess={refetch}
            />
        </div>
    )
}