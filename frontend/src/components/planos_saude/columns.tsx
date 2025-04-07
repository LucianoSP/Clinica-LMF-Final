import { Column } from "@/components/ui/SortableTable";
import { PlanoSaude } from "@/types/plano_saude";
import { formatarData } from "@/lib/utils";

export const columns: Column<PlanoSaude>[] = [
  {
    key: "nome",
    label: "Nome do Plano",
    sortable: true,
  },
  {
    key: "codigo_operadora",
    label: "Código Operadora",
    sortable: true,
  },
  {
    key: "registro_ans",
    label: "Registro ANS",
    sortable: true,
  },
    {
    key: "tipo_plano",
    label: "Tipo do Plano",
    render: (value: unknown) => (value as string) || "-",
  },
  {
    key: "abrangencia",
    label: "Abrangência",
    render: (value: unknown) => (value as string) || "-",
  },
  {
    key: "ativo",
    label: "Status",
    render: (value: unknown) => (value as boolean) ? "Ativo" : "Inativo",
    sortable: true,
  },
  // {
  //   key: "observacoes",
  //   label: "Observações",
  //   render: (value: unknown) => (value as string) || "-",
  // },
  // {
  //   key: "created_at",
  //   label: "Data Cadastro",
  //   render: (value: unknown) => formatarData(value as string),
  //   sortable: true,
  // },
  // {
  //   key: "updated_at",
  //   label: "Última Atualização",
  //   render: (value: unknown) => formatarData(value as string),
  //   sortable: true,
  // }
];