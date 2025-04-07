import { formatarData } from "@/lib/utils";
import { Agendamento } from "@/types/agendamento";
import { ReactNode } from "react";

// Definindo o tipo Column para compatibilidade com SortableTable
export interface Column<T> {
    key: string;
    label: string;
    render: (value: unknown, item: T) => ReactNode;
    visibleByDefault?: boolean;
}

export const columns: Column<Agendamento>[] = [
    {
        key: "data_agendamento",
        label: "Data",
        render: (_, agendamento: Agendamento) => formatarData(agendamento.data_agendamento),
        visibleByDefault: true,
    },
    {
        key: "hora_inicio",
        label: "Hora inicial",
        render: (_, agendamento: Agendamento) => agendamento.hora_inicio,
        visibleByDefault: true,
    },
    {
        key: "hora_fim",
        label: "Hora final",
        render: (_, agendamento: Agendamento) => agendamento.hora_fim,
        visibleByDefault: true,
    },
    {
        key: "paciente_id",
        label: "Paciente",
        render: (_, agendamento: Agendamento) => {
            // Tenta obter informações do paciente
            const pacienteNome = agendamento.paciente_nome || "";
            const carteirinha = agendamento.carteirinha || "";
            
            if (pacienteNome) {
                return (
                    <div className="flex flex-col">
                        <span className="font-medium">{pacienteNome}</span>
                        {carteirinha && (
                            <span className="text-xs text-muted-foreground">{carteirinha}</span>
                        )}
                    </div>
                );
            }
            
            // Se não tiver nome do paciente
            const idPaciente = agendamento.id_origem || agendamento.cod_paciente || "N/A";
            return <span className="text-muted-foreground">ID: {idPaciente}</span>;
        },
        visibleByDefault: true,
    },
    {
        key: "carteirinha",
        label: "Carteirinha",
        render: (_, agendamento: Agendamento) => agendamento.carteirinha || "-",
        visibleByDefault: true,
    },
    {
        key: "procedimento_id",
        label: "Procedimento",
        render: (_, agendamento: Agendamento) => {
            // Tenta obter informações do procedimento
            const procedimentoNome = agendamento.procedimento_nome || "";
            
            if (procedimentoNome) {
                return <span>{procedimentoNome}</span>;
            }
            
            // Se não tiver procedimento
            const codigoFaturamento = agendamento.codigo_faturamento || "";
            if (codigoFaturamento) {
                return <span className="text-muted-foreground">Código: {codigoFaturamento}</span>;
            }
            
            return <span className="text-muted-foreground">N/A</span>;
        },
        visibleByDefault: true,
    },
    {
        key: "profissional",
        label: "Profissional",
        render: (_, agendamento: Agendamento) => agendamento.profissional || "-",
        visibleByDefault: true,
    },
    {
        key: "sala",
        label: "Sala",
        render: (_, agendamento: Agendamento) => agendamento.sala || "-",
        visibleByDefault: true,
    },
    {
        key: "status",
        label: "Status",
        render: (_, agendamento: Agendamento) => {
            const statusMap: Record<string, { label: string, color: string }> = {
                "agendado": { label: "Agendado", color: "bg-blue-100 text-blue-800" },
                "confirmado": { label: "Confirmado", color: "bg-green-100 text-green-800" },
                "cancelado": { label: "Cancelado", color: "bg-red-100 text-red-800" },
                "realizado": { label: "Realizado", color: "bg-purple-100 text-purple-800" },
                "faltou": { label: "Faltou", color: "bg-orange-100 text-orange-800" }
            };
            
            const status = statusMap[agendamento.status?.toLowerCase()] || { 
                label: agendamento.status, 
                color: "bg-gray-100 text-gray-800" 
            };
            
            return (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                    {status.label}
                </span>
            );
        },
        visibleByDefault: true,
    },
    {
        key: "observacoes",
        label: "Observações",
        render: (_, agendamento: Agendamento) => {
            if (!agendamento.observacoes) return "-";
            
            // Se a observação for muito longa, mostrar apenas parte dela
            const maxLength = 50;
            const text = agendamento.observacoes;
            
            if (text.length <= maxLength) return text;
            
            return (
                <span title={text}>
                    {text.substring(0, maxLength)}...
                </span>
            );
        },
        visibleByDefault: true,
    },
    {
        key: "pagamento",
        label: "Pagamento",
        render: (_, agendamento: Agendamento) => {
            const pagamento = agendamento.pagamento || "N/A";
            return <span>{pagamento}</span>;
        },
        visibleByDefault: true,
    },
    {
        key: "id_atendimento",
        label: "Id Atendimento",
        render: (_, agendamento: Agendamento) => agendamento.id_atendimento || agendamento.id_origem || "-",
        visibleByDefault: false,
    },
    {
        key: "unidade",
        label: "Unidade",
        render: (_, agendamento: Agendamento) => agendamento.unidade || "-",
        visibleByDefault: false,
    },
    {
        key: "cod_paciente",
        label: "Cod. Paciente",
        render: (_, agendamento: Agendamento) => agendamento.cod_paciente || "-",
        visibleByDefault: false,
    },
    {
        key: "id_profissional",
        label: "Id Profissional",
        render: (_, agendamento: Agendamento) => agendamento.id_profissional || "-",
        visibleByDefault: false,
    },
    {
        key: "qtd_sess",
        label: "Qtd Sess",
        render: (_, agendamento: Agendamento) => agendamento.qtd_sess?.toString() || "1",
        visibleByDefault: false,
    },
    {
        key: "elegibilidade",
        label: "Elegibilidade",
        render: (_, agendamento: Agendamento) => 
            agendamento.elegibilidade === true ? "Sim" : 
            agendamento.elegibilidade === false ? "Não" : "-",
        visibleByDefault: false,
    },
    {
        key: "substituicao",
        label: "Substituição",
        render: (_, agendamento: Agendamento) => 
            agendamento.substituicao === true ? "Sim" : 
            agendamento.substituicao === false ? "Não" : "-",
        visibleByDefault: false,
    },
    {
        key: "tipo_falta",
        label: "Tipo de Falta",
        render: (_, agendamento: Agendamento) => agendamento.tipo_falta || 
            (agendamento.status?.toLowerCase() === "faltou" ? "N" : "-"),
        visibleByDefault: false,
    },
    {
        key: "id_pai",
        label: "Id Pai",
        render: (_, agendamento: Agendamento) => agendamento.id_pai || "-",
        visibleByDefault: false,
    },
    {
        key: "codigo_faturamento",
        label: "Código Faturamento",
        render: (_, agendamento: Agendamento) => agendamento.codigo_faturamento || "-",
        visibleByDefault: false,
    },
]; 