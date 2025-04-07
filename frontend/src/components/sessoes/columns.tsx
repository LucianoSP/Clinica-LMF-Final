import { ColumnDef } from "@tanstack/react-table";
import { Sessao } from "@/types/sessao";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/utils/date";
import { MoreHorizontal } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export const columns: ColumnDef<Sessao>[] = [
    {
        accessorKey: "data_sessao",
        header: "Data",
        cell: ({ row }) => {
            const data = row.getValue("data_sessao") as string;
            return formatDate(data);
        },
    },
    {
        accessorKey: "hora_inicio",
        header: "Hora Início",
    },
    {
        accessorKey: "hora_fim",
        header: "Hora Fim",
    },
    {
        accessorKey: "tipo_atendimento",
        header: "Tipo",
        cell: ({ row }) => {
            const tipo = row.getValue("tipo_atendimento") as string;
            return tipo === "presencial" ? "Presencial" : "Teleconsulta";
        },
    },
    {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => {
            const status = row.getValue("status") as string;
            const statusMap = {
                agendada: "Agendada",
                realizada: "Realizada",
                cancelada: "Cancelada",
                faltou: "Faltou"
            };
            return statusMap[status as keyof typeof statusMap] || status;
        },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const sessao = row.original;

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuItem
                            onClick={() => console.log('Editar', sessao)}
                        >
                            Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            onClick={() => console.log('Excluir', sessao)}
                            className="text-red-600"
                        >
                            Excluir
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
]; 