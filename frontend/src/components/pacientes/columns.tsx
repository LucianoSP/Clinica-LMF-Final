import { Column } from "@/components/ui/SortableTable";
import { Paciente } from "@/types/paciente";
import { formatarData } from "@/lib/utils";

export const columns: Column<Paciente>[] = [
  {
    key: "nome",
    label: "Nome",
    sortable: true,
  },
  {
    key: "nome_responsavel",
    label: "Responsável",
    sortable: true,
  },
  {
    key: "cpf",
    label: "CPF",
    render: (value: unknown, _: Paciente) => (value as string) || "-",
    sortable: true,
  },
  {
    key: "rg",
    label: "RG",
    render: (value: unknown) => (value as string) || "-",
    sortable: true,
  },
  {
    key: "data_nascimento",
    label: "Data Nasc.",
    render: (value: unknown) => formatarData(value as string) || "-",
    sortable: true,
  },
  {
    key: "telefone",
    label: "Telefone",
    render: (value: unknown) => (value as string) || "-",
    sortable: true,
  },
  {
    key: "email",
    label: "Email",
    render: (value: unknown) => (value as string) || "-",
    sortable: true,
  },
  {
    key: "cidade",
    label: "Cidade",
    render: (value: unknown) => (value as string) || "-",
    sortable: true,
  },
  {
    key: "data_registro_origem",
    label: "Data Cadastro",
    render: (value: unknown) => formatarData(value as string),
    sortable: true,
  }
];
