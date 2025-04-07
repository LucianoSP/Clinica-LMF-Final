import { Execucao, BiometriaStatus } from "@/types/execucao";
import { BadgeStatus } from "@/components/ui/badge-status";
import { formatarData } from "@/lib/utils";
import { Column } from "@/components/ui/SortableTable";
import { ReactNode } from "react";
import { CheckCircle, XCircle, HelpCircle, User, FileText } from "lucide-react";
import { BadgeBiometria } from "./BadgeBiometria";

export const columns: Column<Execucao>[] = [
    {
        key: "paciente_nome",
        label: "Paciente",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Verificar se o campo existe e tem valor
            return item.paciente_nome || "Não informado";
        },
    },
    {
        key: "data_atendimento",
        label: "Data de Atendimento",
        render: (value: unknown, item: Execucao): ReactNode => {
            if (item.data_atendimento) return formatarData(item.data_atendimento);
            // Se não tiver data de atendimento, usa a data de execução
            if (item.data_execucao) return formatarData(item.data_execucao);
            return "-";
        },
    },
    {
        key: "data_execucao",
        label: "Data de Execução",
        render: (value: unknown, item: Execucao): ReactNode => {
            if (item.data_execucao) return formatarData(item.data_execucao);
            return "-";
        },
    },
    {
        key: "paciente_carteirinha",
        label: "Carteirinha",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Verificar se o campo existe e tem valor
            return item.paciente_carteirinha || "Não informado";
        },
    },
    {
        key: "numero_guia",
        label: "Nº Guia",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Verificar se o campo existe e tem valor
            if (item.numero_guia) return item.numero_guia;
            // Se não tiver número de guia, usa o ID da guia como alternativa
            if (item.guia_id) return `GUIA-${item.guia_id.substring(0, 6)}`;
            return "Não informado";
        },
    },
    {
        key: "codigo_ficha",
        label: "Código da Ficha",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Verificar se o campo existe e tem valor
            if (item.codigo_ficha) return item.codigo_ficha;
            // Se não tiver código de ficha, usa o ID como alternativa
            return `FICHA-${item.id.substring(0, 8)}`;
        },
    },
    {
        key: "origem",
        label: "Origem",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Verificar se o campo existe e tem valor
            return item.origem || "Sistema";
        },
    },
    {
        key: "status_biometria",
        label: "Biometria",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Usar o componente BadgeBiometria para exibir o status
            return <BadgeBiometria value={item.status_biometria} />;
        },
    },
    {
        key: "profissional_executante",
        label: "Profissional Executante",
        render: (value: unknown, item: Execucao): ReactNode => {
            // Verificar se o campo existe e tem valor
            if (item.profissional_executante) return item.profissional_executante;
            
            // Se tiver ID do profissional, usamos ele como referência
            if (item.profissional_id) {
                return (
                    <div className="flex items-center text-gray-500">
                        <User className="h-4 w-4 mr-1" />
                        <span>Prof. {item.profissional_id.substring(0, 6)}</span>
                    </div>
                );
            }
            
            // Se tiver usuario_executante, usamos ele como referência
            if (item.usuario_executante) {
                return (
                    <div className="flex items-center text-gray-500">
                        <User className="h-4 w-4 mr-1" />
                        <span>Usuário {item.usuario_executante.substring(0, 6)}</span>
                    </div>
                );
            }
            
            return "Não informado";
        },
    },
    {
        key: "status",
        label: "Status",
        render: (value: unknown, item: Execucao): ReactNode => {
            if (item.status) {
                return <BadgeStatus value={item.status} />;
            }
            return <BadgeStatus value="pendente" />;
        },
    }
];