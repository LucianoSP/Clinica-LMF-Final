"use client"

import { Column } from "@/components/ui/SortableTable";
import { Storage } from "@/types/storage"
import { formatarData } from "@/lib/utils"
import { formatBytes } from "@/lib/formatters"
import { Download, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";

export const columns: Column<Storage>[] = [
    {
        key: "nome",
        label: "Nome",
        sortable: true,
    },
    {
        key: "size",
        label: "Tamanho",
        sortable: true,
        render: (value: unknown) => formatBytes(value as number),
    },
    {
        key: "created_at",
        label: "Data de Criação",
        sortable: true,
        render: (value: unknown) => formatarData(value as string, true),
    },
    {
        key: "actions",
        label: "Ações",
        sortable: false,
        render: (_, row) => (
            <div className="flex items-center gap-2">
                <Button
                    variant="ghost"
                    size="icon"
                    asChild
                    className="h-8 w-8 p-0"
                >
                    <a href={row.url} target="_blank" rel="noopener noreferrer" download>
                        <Download className="h-4 w-4" />
                    </a>
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 p-0"
                >
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </div>
        ),
    },
]