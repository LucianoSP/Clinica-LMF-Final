import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { GuiaFormData } from "@/types/guia"
import { usePacientes } from "@/hooks/usePacientes"
import { useCarteirinhas } from "@/hooks/useCarteirinhas"
import { useProcedimentos } from "@/hooks/useProcedimentos"

const tipoOptions = [
    { value: 'consulta', label: 'Consulta' },
    { value: 'exame', label: 'Exame' },
    { value: 'procedimento', label: 'Procedimento' },
    { value: 'internacao', label: 'Internação' },
] as const

const statusOptions = [
    { value: 'rascunho', label: 'Rascunho' },
    { value: 'pendente', label: 'Pendente' },
    { value: 'autorizada', label: 'Autorizada' },
    { value: 'negada', label: 'Negada' },
    { value: 'cancelada', label: 'Cancelada' },
    { value: 'executada', label: 'Executada' },
] as const

const formSchema = z.object({
    numero_guia: z.string().min(1, "Número da guia é obrigatório"),
    senha_autorizacao: z.string().optional(),
    data_emissao: z.string().optional(),
    data_validade: z.string().optional(),
    data_autorizacao: z.string().optional(),
    data_validade_senha: z.string().optional(),
    tipo: z.enum(['consulta', 'exame', 'procedimento', 'internacao']),
    status: z.enum(['rascunho', 'pendente', 'autorizada', 'negada', 'cancelada', 'executada']),
    carteirinha_id: z.string().min(1, "Carteirinha é obrigatória"),
    paciente_id: z.string().min(1, "Paciente é obrigatório"),
    procedimento_id: z.string().min(1, "Procedimento é obrigatório"),
    quantidade_autorizada: z.number().min(1, "Quantidade autorizada deve ser maior que zero"),
    quantidade_executada: z.number().optional(),
    valor_autorizado: z.number().optional(),
    profissional_solicitante: z.string().optional(),
    profissional_executante: z.string().optional(),
    observacoes: z.string().optional(),
})

interface GuiaFormProps {
    guia?: GuiaFormData
    onSubmit: (data: GuiaFormData) => void
    onCancel: () => void
}

export function GuiaForm({ guia, onSubmit, onCancel }: GuiaFormProps) {
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: guia || {
            status: 'rascunho',
            quantidade_executada: 0,
        },
    })

    const { data: pacientesData } = usePacientes(1, 100)
    const { data: carteirinhasData } = useCarteirinhas(1, 100)
    const { data: procedimentosData } = useProcedimentos(1, 100)

    const handleSubmit = (data: z.infer<typeof formSchema>) => {
        onSubmit(data as GuiaFormData)
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="numero_guia"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Número da Guia</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="tipo"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Tipo</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Selecione o tipo" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {tipoOptions.map((option) => (
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
                        name="data_emissao"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Data de Emissão</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="data_validade"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Data de Validade</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="carteirinha_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Carteirinha</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Selecione a carteirinha" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {carteirinhasData?.items.map((carteirinha) => (
                                            <SelectItem key={carteirinha.id} value={carteirinha.id}>
                                                {carteirinha.numero_carteirinha}
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
                        name="paciente_id"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Paciente</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Selecione o paciente" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        {pacientesData?.items.map((paciente) => (
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
                </div>

                <FormField
                    control={form.control}
                    name="procedimento_id"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Procedimento</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Selecione o procedimento" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    {procedimentosData?.items.map((procedimento) => (
                                        <SelectItem key={procedimento.id} value={procedimento.id}>
                                            {procedimento.nome}
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
                        name="quantidade_autorizada"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Quantidade Autorizada</FormLabel>
                                <FormControl>
                                    <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="quantidade_executada"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Quantidade Executada</FormLabel>
                                <FormControl>
                                    <Input type="number" {...field} onChange={e => field.onChange(Number(e.target.value))} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="valor_autorizado"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Valor Autorizado</FormLabel>
                            <FormControl>
                                <Input 
                                    type="number" 
                                    step="0.01" 
                                    {...field} 
                                    onChange={e => field.onChange(Number(e.target.value))} 
                                />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="profissional_solicitante"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Profissional Solicitante</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="profissional_executante"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Profissional Executante</FormLabel>
                                <FormControl>
                                    <Input {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

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

                <div className="flex justify-end space-x-4">
                    <Button type="button" variant="outline" onClick={onCancel}>
                        Cancelar
                    </Button>
                    <Button type="submit">
                        {guia ? 'Atualizar' : 'Criar'} Guia
                    </Button>
                </div>
            </form>
        </Form>
    )
} 