"use client"

import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react"
import { Guia } from "@/types/guia"
import { useState } from "react"
import { GuiaModal } from "./GuiaModal"
import { useToast } from "@/components/ui/use-toast"
import { guiaService } from "@/services/guiaService"
import { useQueryClient } from "@tanstack/react-query"

interface DataTableRowActionsProps {
    row: {
        original: Guia
    }
}

export function DataTableRowActions({ row }: DataTableRowActionsProps) {
    const [isEditModalOpen, setIsEditModalOpen] = useState(false)
    const { toast } = useToast()
    const queryClient = useQueryClient()

    const handleDelete = async () => {
        try {
            await guiaService.excluir(row.original.id)
            await queryClient.invalidateQueries({ queryKey: ['guias'] })
            toast({
                title: "Guia excluída",
                description: "A guia foi excluída com sucesso.",
            })
        } catch (error) {
            console.error('Erro ao excluir guia:', error)
            toast({
                title: "Erro ao excluir",
                description: "Ocorreu um erro ao excluir a guia.",
                variant: "destructive",
            })
        }
    }

    return (
        <>
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Abrir menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setIsEditModalOpen(true)}>
                        <Pencil className="mr-2 h-4 w-4" />
                        Editar
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleDelete}>
                        <Trash2 className="mr-2 h-4 w-4" />
                        Excluir
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>

            <GuiaModal
                open={isEditModalOpen}
                onOpenChange={setIsEditModalOpen}
                initialData={row.original}
            />
        </>
    )
}
