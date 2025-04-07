import { Column } from "@/components/ui/SortableTable";
import { formatarData } from "@/lib/utils";
import { Carteirinha, CarteirinhaStatus } from "@/types/carteirinha";
import { ReactNode } from "react";
import { BadgeCarteirinhaStatus } from "@/components/ui/badge-carteirinha-status";

export const columns: Column<Carteirinha>[] = [
  {
    key: "plano_saude_nome",
    label: "Plano de Saúde",
    render: (value, item): ReactNode => value as string || "-",
    sortable: true,
  },
  {
    key: "paciente_nome",
    label: "Paciente",
    render: (value, item): ReactNode => value as string || "-",
    sortable: true,
  },
  {
    key: "numero_carteirinha",
    label: "Número",
    sortable: true,
  },
  {
    key: "data_validade",
    label: "Validade",
    render: (value, item): ReactNode => formatarData(value as string) || "-",
    sortable: true,
  },
  {
    key: "status",
    label: "Status",
    render: (value, item: Carteirinha): ReactNode => {
      const status = value?.toString().toLowerCase() as CarteirinhaStatus;
      return <BadgeCarteirinhaStatus value={status} />;
    },
    sortable: true,
  },
  {
    key: "created_at",
    label: "Data Cadastro",
    render: (value, item): ReactNode => formatarData(value as string) || "-",
    sortable: true,
  }
];
