"use client"

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Execucao, StatusExecucao, TipoExecucao } from "@/types/execucao";
import { usePacientes } from "@/hooks/usePacientes";
import { useGuiasPorPaciente } from "@/hooks/useGuias";
import { useSessoesDaGuia } from "@/hooks/useSessoes";
import { Sessao } from "@/types/sessao";
import { Guia } from "@/types/guia";
import { Paciente } from "@/types/paciente";
import { PaginatedResponse, StandardResponse } from "@/types/api";
import { formatarData } from "@/lib/utils";

const schema = z.object({
    sessao_id: z.string().min(1, "Sessão é obrigatória"),
    guia_id: z.string().min(1, "Guia é obrigatória"),
    paciente_id: z.string().min(1, "Paciente é obrigatório"),
    data_execucao: z.string().min(1, "Data de execução é obrigatória"),
    hora_inicio: z.string().optional(),
    hora_fim: z.string().optional(),
    status: z.enum(["pendente", "realizada", "cancelada"]).default("pendente"),
    tipo_execucao: z.enum(["presencial", "teleconsulta"]),
    procedimentos: z.array(z.any()).default([]),
    valor_total: z.number().optional(),
    assinatura_paciente: z.string().optional(),
    assinatura_profissional: z.string().optional(),
    observacoes: z.string().optional(),
    anexos: z.array(z.any()).default([])
});

export type ExecucaoFormData = z.infer<typeof schema>;

const statusOptions = [
    { value: 'pendente', label: 'Pendente' },
    { value: 'realizada', label: 'Realizada' },
    { value: 'cancelada', label: 'Cancelada' }
];

const tipoExecucaoOptions = [
    { value: 'presencial', label: 'Presencial' },
    { value: 'teleconsulta', label: 'Teleconsulta' }
];

interface ExecucaoFormProps {
    onSubmit: (data: ExecucaoFormData) => Promise<void>;
    execucao?: Execucao;
}

export function ExecucaoForm({ onSubmit, execucao }: ExecucaoFormProps) {
    const [selectedPacienteId, setSelectedPacienteId] = useState<string>(execucao?.paciente_id || "");
    const [selectedGuiaId, setSelectedGuiaId] = useState<string>(execucao?.guia_id || "");

    const { data: pacientesData } = usePacientes(1, 100);
    const { data: guiasData } = useGuiasPorPaciente(selectedPacienteId);
    const { data: sessoesData } = useSessoesDaGuia(selectedGuiaId);

    const form = useForm<ExecucaoFormData>({
        resolver: zodResolver(schema),
        defaultValues: execucao ? {
            sessao_id: execucao.sessao_id || "",
            guia_id: execucao.guia_id,
            paciente_id: execucao.paciente_id || "",
            data_execucao: execucao.data_execucao,
            hora_inicio: execucao.hora_inicio || "",
            hora_fim: execucao.hora_fim || "",
            status: execucao.status,
            tipo_execucao: execucao.tipo_execucao || "presencial",
            procedimentos: execucao.procedimentos || [],
            valor_total: execucao.valor_total === null ? undefined : execucao.valor_total,
            assinatura_paciente: execucao.assinatura_paciente || undefined,
            assinatura_profissional: execucao.assinatura_profissional || undefined,
            observacoes: execucao.observacoes || undefined,
            anexos: execucao.anexos || []
        } : {
            sessao_id: "",
            guia_id: "",
            paciente_id: "",
            data_execucao: new Date().toISOString().split('T')[0],
            hora_inicio: "",
            hora_fim: "",
            status: "pendente",
            tipo_execucao: "presencial",
            procedimentos: [],
            valor_total: undefined,
            assinatura_paciente: undefined,
            assinatura_profissional: undefined,
            observacoes: undefined,
            anexos: []
        }
    });

    const handleSubmit = async (data: ExecucaoFormData) => {
        try {
            await onSubmit(data);
        } catch (error) {
            console.error('Erro ao salvar execução:', error);
        }
    };

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
                <FormField
                    control={form.control}
                    name="paciente_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Paciente</FormLabel>
                            <Select 
                                onValueChange={(value) => {
                                    field.onChange(value);
                                    setSelectedPacienteId(value);
                                    // Limpa os campos dependentes
                                    form.setValue('guia_id', '');
                                    form.setValue('sessao_id', '');
                                }} 
                                defaultValue={field.value}
                            >
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Selecione um paciente" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {pacientesData?.items?.map((paciente: Paciente) => (
                                        <SelectItem key={paciente.id} value={paciente.id}>
                                            {paciente.nome}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="guia_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Guia</FormLabel>
                            <Select 
                                onValueChange={(value) => {
                                    field.onChange(value);
                                    setSelectedGuiaId(value);
                                    // Limpa o campo de sessão
                                    form.setValue('sessao_id', '');
                                }} 
                                defaultValue={field.value}
                                disabled={!selectedPacienteId}
                            >
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Selecione uma guia" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {guiasData?.data?.map((guia: Guia) => (
                                        <SelectItem key={guia.id} value={guia.id}>
                                            {guia.numero_guia}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="sessao_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Sessão</FormLabel>
                            <Select 
                                onValueChange={field.onChange} 
                                defaultValue={field.value}
                                disabled={!selectedGuiaId}
                            >
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Selecione uma sessão" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {sessoesData?.data?.map((sessao: Sessao) => (
                                        <SelectItem key={sessao.id} value={sessao.id}>
                                            {`Sessão - ${formatarData(sessao.data_sessao)}`}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="data_execucao"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Data de Execução</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="status"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Status</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Selecione o status" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {statusOptions.map((option) => (
                                            <SelectItem key={option.value} value={option.value}>
                                                {option.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="hora_inicio"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Hora Início</FormLabel>
                                <FormControl>
                                    <Input type="time" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="hora_fim"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Hora Fim</FormLabel>
                                <FormControl>
                                    <Input type="time" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="tipo_execucao"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Tipo de Execução</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Selecione o tipo de execução" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {tipoExecucaoOptions.map((option) => (
                                        <SelectItem key={option.value} value={option.value}>
                                            {option.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="observacoes"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Observações</FormLabel>
                            <FormControl>
                                <Input {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end space-x-2">
                    <Button type="submit">
                        {execucao ? "Atualizar" : "Criar"} Execução
                    </Button>
                </div>
            </form>
        </Form>
    );
}