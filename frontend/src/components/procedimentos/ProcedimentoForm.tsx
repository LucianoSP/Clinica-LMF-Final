import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Procedimento, ProcedimentoCreate } from "@/types/procedimento";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const procedimentoSchema = z.object({
    codigo: z.string().min(1, "Código é obrigatório").max(20, "Código deve ter no máximo 20 caracteres"),
    nome: z.string().min(1, "Nome é obrigatório"),
    descricao: z.string().optional(),
    tipo: z.string().min(1, "Tipo é obrigatório"),
    valor: z.string()
        .transform((val) => {
            if (!val) return undefined;
            // Remove os separadores de milhar e converte vírgula para ponto
            const num = parseFloat(val.replace(/\./g, '').replace(',', '.'));
            return isNaN(num) ? undefined : num;
        })
        .optional(),
    valor_filme: z.string()
        .transform((val) => {
            if (!val) return undefined;
            const num = parseFloat(val.replace(/\./g, '').replace(',', '.'));
            return isNaN(num) ? undefined : num;
        })
        .optional(),
    valor_operacional: z.string()
        .transform((val) => {
            if (!val) return undefined;
            const num = parseFloat(val.replace(/\./g, '').replace(',', '.'));
            return isNaN(num) ? undefined : num;
        })
        .optional(),
    valor_total: z.string()
        .transform((val) => {
            if (!val) return undefined;
            const num = parseFloat(val.replace(/\./g, '').replace(',', '.'));
            return isNaN(num) ? undefined : num;
        })
        .optional(),
    tempo_medio_execucao: z.string()
        .nullable()
        .transform((val) => {
            if (!val) return null;
            const minutes = parseInt(val);
            if (isNaN(minutes) || minutes < 0) return null;
            return minutes.toString();
        })
        .optional(),
    requer_autorizacao: z.boolean(),
    observacoes: z.string().optional(),
    ativo: z.boolean()
});

interface ProcedimentoFormProps {
    onSubmit: (data: ProcedimentoCreate) => Promise<void>;
    procedimento?: Procedimento;
    loading?: boolean;
    id?: string;
}

const TIPOS_PROCEDIMENTO = [
    "consulta",
    "exame",
    "procedimento",
    "internacao"
];

export function ProcedimentoForm({ onSubmit, procedimento, loading, id }: ProcedimentoFormProps) {
    const form = useForm<ProcedimentoCreate>({
        resolver: zodResolver(procedimentoSchema),
        defaultValues: {
            codigo: procedimento?.codigo ?? "",
            nome: procedimento?.nome ?? "",
            descricao: procedimento?.descricao ?? "",
            tipo: procedimento?.tipo ?? undefined,
            valor: procedimento?.valor?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "",
            valor_filme: procedimento?.valor_filme?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "",
            valor_operacional: procedimento?.valor_operacional?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "",
            valor_total: procedimento?.valor_total?.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "",
            tempo_medio_execucao: procedimento?.tempo_medio_execucao ?? "",
            requer_autorizacao: procedimento?.requer_autorizacao ?? true,
            observacoes: procedimento?.observacoes ?? "",
            ativo: procedimento?.ativo ?? true
        }
    });

    return (
        <Form {...form}>
            <form id={id} onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="codigo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Código</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="tipo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tipo</FormLabel>
                                <Select
                                    onValueChange={field.onChange}
                                    defaultValue={field.value}
                                >
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Selecione um tipo" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {TIPOS_PROCEDIMENTO.map((tipo) => (
                                            <SelectItem key={tipo} value={tipo}>
                                                {tipo}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="nome"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Nome</FormLabel>
                            <FormControl>
                                <Input {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="descricao"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Descrição</FormLabel>
                            <FormControl>
                                <Textarea {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="valor"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Valor Base</FormLabel>
                                <FormControl>
                                    <Input
                                        type="text"
                                        inputMode="decimal"
                                        {...field}
                                        value={field.value || ''}
                                        onChange={(e) => {
                                            let value = e.target.value.replace(/[^0-9,]/g, '');
                                            // Garante apenas uma vírgula
                                            const matches = value.match(/,/g);
                                            if (matches && matches.length > 1) {
                                                value = value.substring(0, value.lastIndexOf(','));
                                            }
                                            field.onChange(value);
                                        }}
                                        onBlur={(e) => {
                                            if (!e.target.value) return;
                                            // Formata o número com duas casas decimais
                                            const num = parseFloat(e.target.value.replace(',', '.'));
                                            if (!isNaN(num)) {
                                                field.onChange(num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
                                            }
                                        }}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="valor_filme"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Valor do Filme</FormLabel>
                                <FormControl>
                                    <Input
                                        type="text"
                                        inputMode="decimal"
                                        {...field}
                                        value={field.value || ''}
                                        onChange={(e) => {
                                            let value = e.target.value.replace(/[^0-9,]/g, '');
                                            // Garante apenas uma vírgula
                                            const matches = value.match(/,/g);
                                            if (matches && matches.length > 1) {
                                                value = value.substring(0, value.lastIndexOf(','));
                                            }
                                            field.onChange(value);
                                        }}
                                        onBlur={(e) => {
                                            if (!e.target.value) return;
                                            // Formata o número com duas casas decimais
                                            const num = parseFloat(e.target.value.replace(',', '.'));
                                            if (!isNaN(num)) {
                                                field.onChange(num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
                                            }
                                        }}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="valor_operacional"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Valor Operacional</FormLabel>
                                <FormControl>
                                    <Input
                                        type="text"
                                        inputMode="decimal"
                                        {...field}
                                        value={field.value || ''}
                                        onChange={(e) => {
                                            let value = e.target.value.replace(/[^0-9,]/g, '');
                                            // Garante apenas uma vírgula
                                            const matches = value.match(/,/g);
                                            if (matches && matches.length > 1) {
                                                value = value.substring(0, value.lastIndexOf(','));
                                            }
                                            field.onChange(value);
                                        }}
                                        onBlur={(e) => {
                                            if (!e.target.value) return;
                                            // Formata o número com duas casas decimais
                                            const num = parseFloat(e.target.value.replace(',', '.'));
                                            if (!isNaN(num)) {
                                                field.onChange(num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
                                            }
                                        }}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="valor_total"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Valor Total</FormLabel>
                                <FormControl>
                                    <Input
                                        type="text"
                                        inputMode="decimal"
                                        {...field}
                                        value={field.value || ''}
                                        onChange={(e) => {
                                            let value = e.target.value.replace(/[^0-9,]/g, '');
                                            // Garante apenas uma vírgula
                                            const matches = value.match(/,/g);
                                            if (matches && matches.length > 1) {
                                                value = value.substring(0, value.lastIndexOf(','));
                                            }
                                            field.onChange(value);
                                        }}
                                        onBlur={(e) => {
                                            if (!e.target.value) return;
                                            // Formata o número com duas casas decimais
                                            const num = parseFloat(e.target.value.replace(',', '.'));
                                            if (!isNaN(num)) {
                                                field.onChange(num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
                                            }
                                        }}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="tempo_medio_execucao"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Tempo Médio de Execução (minutos)</FormLabel>
                            <FormControl>
                                <Input 
                                    type="number" 
                                    min="0"
                                    {...field}
                                    value={field.value || ''}
                                    onChange={(e) => {
                                        const minutes = parseInt(e.target.value);
                                        field.onChange(minutes < 0 ? null : e.target.value);
                                    }}
                                />
                            </FormControl>
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
                                <Textarea {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex items-center gap-8">
                    <FormField
                        control={form.control}
                        name="requer_autorizacao"
                        render={({ field }) => (
                            <FormItem className="flex items-center gap-2">
                                <FormControl>
                                    <Switch
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                    />
                                </FormControl>
                                <FormLabel className="!mt-0">Requer Autorização</FormLabel>
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="ativo"
                        render={({ field }) => (
                            <FormItem className="flex items-center gap-2">
                                <FormControl>
                                    <Switch
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                    />
                                </FormControl>
                                <FormLabel className="!mt-0">Ativo</FormLabel>
                            </FormItem>
                        )}
                    />
                </div>
            </form>
        </Form>
    );
} 