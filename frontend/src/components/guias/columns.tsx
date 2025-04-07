import { Column } from "@/components/ui/SortableTable"
import { formatarData } from "@/lib/utils"
import { Guia, GuiaStatus, TipoGuia } from "@/types/guia"
import { BadgeGuiaStatus } from "@/components/ui/badge-guia-status"
import { ReactNode } from "react"
import { DataTableRowActions } from "./guia-row-actions"

export const columns: Column<Guia>[] = [
    {
        key: "numero_guia",
        label: "Número",
        sortable: true,
    },
    {
        key: "paciente_nome",
        label: "Paciente",
        sortable: true,
        render: (_: unknown, row: Guia): ReactNode => {
            return row.paciente_nome || "-";
        },
    },
    {
        key: "carteirinha_numero",
        label: "Carteirinha",
        sortable: true,
        render: (_: unknown, row: Guia): ReactNode => {
            return row.carteirinha_numero || "-";
        },
    },
    {
        key: "tipo",
        label: "Tipo",
        sortable: true,
        render: (value: unknown, _: Guia): ReactNode => {
            const tipo = value?.toString().toLowerCase() as TipoGuia;
            return <BadgeGuiaStatus value={tipo} />;
        },
    },
    {
        key: "status",
        label: "Status",
        sortable: true,
        render: (value: unknown, _: Guia): ReactNode => {
            const status = value?.toString().toLowerCase() as GuiaStatus;
            return <BadgeGuiaStatus value={status} />;
        },
    },
    {
        key: "data_solicitacao",
        label: "Data Solicitação",
        sortable: true,
        render: (value: unknown, row: Guia): ReactNode => {
            if (!value) return "-";
            try {
                return formatarData(value as string) || "-";
            } catch (error) {
                console.error('Erro ao formatar data de solicitação:', error);
                return "-";
            }
        },
    },
    {
        key: "data_autorizacao",
        label: "Data Autorização",
        sortable: true,
        render: (value: unknown, row: Guia): ReactNode => {
            if (row.status !== "autorizada") return "-";
            try {
                const data = row.dados_autorizacao?.data_autorizacao;
                return formatarData(data) || "-";
            } catch (error) {
                console.error('Erro ao formatar data de autorização:', error);
                return "-";
            }
        },
    },
    {
        key: "quantidade_autorizada",
        label: "Qtd. Autorizada",
        sortable: true,
    },
    {
        key: "quantidade_executada",
        label: "Qtd. Executada",
        sortable: true,
    },
    {
        key: "actions",
        label: "Ações",
        render: (_: unknown, item: Guia): ReactNode => {
            return <DataTableRowActions row={{ original: item }} />;
        }
    },
]