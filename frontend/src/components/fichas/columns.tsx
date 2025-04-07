import { Column } from "@/components/ui/SortableTable";
import { Ficha } from "@/types/ficha";
import { formatarData } from "@/lib/utils";
import { BadgeStatus } from "@/components/ui/badge-status";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, ListFilter } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ActionsColumnProps {
    onEdit?: (ficha: Ficha) => void;
    onDelete?: (id: string) => void;
    onViewSessoes?: (ficha: Ficha) => void;
}

export const createColumns = ({ onEdit, onDelete, onViewSessoes }: ActionsColumnProps): Column<Ficha>[] => [
    {
        key: "codigo_ficha",
        label: "Código",
        sortable: true,
    },
    {
        key: "numero_guia",
        label: "Nº Guia",
        sortable: true,
    },
    {
        key: "paciente_nome",
        label: "Paciente",
        sortable: true,
    },
    {
        key: "paciente_carteirinha",
        label: "Carteirinha",
        sortable: true,
    },
    {
        key: "data_atendimento",
        label: "Data Atendimento",
        render: (value: unknown) => formatarData(value as string),
        sortable: true,
    },
    {
        key: "total_sessoes",
        label: "Sessões",
        render: (value: unknown) => value ? value.toString() : '0',
        sortable: true,
    },
    {
        key: "status",
        label: "Status",
        render: (value: unknown) => {
            const status = value as string;
            return (
                <BadgeStatus value={status as any} />
            );
        },
        sortable: true,
    },
    {
        key: "created_at",
        label: "Data Criação",
        render: (value: unknown) => formatarData(value as string),
        sortable: true,
    },
    {
        key: "actions",
        label: "",
        render: (_: unknown, ficha: Ficha) => {
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Abrir menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        {onViewSessoes && (
                            <DropdownMenuItem onClick={() => onViewSessoes(ficha)}>
                                <ListFilter className="mr-2 h-4 w-4" />
                                Editar Sessões
                            </DropdownMenuItem>
                        )}
                        <DropdownMenuItem onClick={() => onEdit?.(ficha)}>
                            Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                            onClick={() => onDelete?.(ficha.id)}
                            className="text-red-600"
                        >
                            Excluir
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        }
    }
];