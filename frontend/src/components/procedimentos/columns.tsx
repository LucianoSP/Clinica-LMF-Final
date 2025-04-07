import { Procedimento } from "@/types/procedimento";
import { formatCurrency } from "@/lib/utils";
import { Column } from "@/components/ui/SortableTable";
import { ReactNode } from "react";

export const columns: Column<Procedimento>[] = [
    {
        key: "codigo",
        label: "Código",
        render: (value: unknown, item: Procedimento): ReactNode => value as string,
    },
    {
        key: "nome",
        label: "Nome",
        render: (value: unknown, item: Procedimento): ReactNode => value as string,
    },
    {
        key: "tipo",
        label: "Tipo",
        render: (value: unknown, item: Procedimento): ReactNode => value as string,
    },
    {
        key: "valor_total",
        label: "Valor Total",
        render: (value: unknown, item: Procedimento): ReactNode => formatCurrency(value as number | string),
    },
    {
        key: "requer_autorizacao",
        label: "Requer Autorização",
        render: (value: unknown, item: Procedimento): ReactNode => (value as boolean) ? "Sim" : "Não",
    },
    {
        key: "ativo",
        label: "Status",
        render: (value: unknown, item: Procedimento): ReactNode => (value as boolean) ? "Ativo" : "Inativo",
    },
    {
        key: "created_at",
        label: "Data de Criação",
        render: (value: unknown, item: Procedimento): ReactNode => new Date(value as string).toLocaleString(),
    },
]; 