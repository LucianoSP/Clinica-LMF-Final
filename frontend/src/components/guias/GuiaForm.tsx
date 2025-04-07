import { useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Guia, GuiaStatus, TipoGuia } from "@/types/guia";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { ComboboxField } from "@/components/ui/combobox-field"; // Importar o novo componente
import { useCarteirinhas } from "@/hooks/useCarteirinhas";
import { usePacientes } from "@/hooks/usePacientes";
import { useProcedimentos } from "@/hooks/useProcedimentos";
import { useState, useEffect } from "react";
import { useDebounce } from "@/hooks/useDebounce";
import { pacienteService } from "@/services/pacienteService";
import { carteirinhaService } from "@/services/carteirinhaService";
import { procedimentoService } from "@/services/procedimentoService";
import { Paciente } from "@/types/paciente";
import { Carteirinha } from "@/types/carteirinha";
import { Procedimento } from "@/types/procedimento";
import { Loader2 } from "lucide-react";
import { guiaService } from "@/services/guiaService";
import { planoSaudeService } from "@/services/planoSaudeService"; // Importar o serviço de plano de saúde

interface CarteirinhaComPlano extends Carteirinha {
    plano_nome?: string;
}

const guiaSchema = z.object({
    carteirinha_id: z.string().min(1, "Carteirinha é obrigatória"),
    paciente_id: z.string().min(1, "Paciente é obrigatório"),
    procedimento_id: z.string().min(1, "Procedimento é obrigatório"),
    numero_guia: z.string().min(1, "Número da guia é obrigatório"),
    tipo: z.enum(["consulta", "exame", "procedimento", "internacao"], {
        required_error: "Tipo é obrigatório",
    }),
    status: z.enum(["rascunho", "pendente", "autorizada", "negada", "executada", "cancelada"], {
        required_error: "Status é obrigatório",
    }),
    data_solicitacao: z.string().min(1, "Data de solicitação é obrigatória"),
    quantidade_solicitada: z.number().min(1, "Quantidade solicitada deve ser maior que 0"),
    quantidade_autorizada: z.number().optional(),
    quantidade_executada: z.number().optional(),
    motivo_negacao: z.string().optional(),
    observacoes: z.string().optional(),
    dados_autorizacao: z.object({
        autorizador: z.string(),
        codigo_autorizacao: z.string(),
        data_autorizacao: z.string(),
    }).optional(),
});

type GuiaFormData = z.infer<typeof guiaSchema>;

export interface GuiaFormProps {
    onSuccess?: () => void;
    onCancel?: () => void;
    initialData?: Guia;
    disabled?: boolean;
    id?: string;
    onSubmit?: () => void;
}

export function GuiaForm({
    onSuccess,
    onCancel,
    initialData,
    disabled = false,
    id,
    onSubmit
}: GuiaFormProps): JSX.Element {
    const [searchCarteirinha, setSearchCarteirinha] = useState("");
    const [searchPaciente, setSearchPaciente] = useState("");
    const [searchProcedimento, setSearchProcedimento] = useState("");
    const [selectedPaciente, setSelectedPaciente] = useState<Paciente | null>(null);
    const [selectedCarteirinha, setSelectedCarteirinha] = useState<CarteirinhaComPlano | null>(null);
    const [selectedProcedimento, setSelectedProcedimento] = useState<Procedimento | null>(null);
    const [carteirinhasDisponiveis, setCarteirinhasDisponiveis] = useState<CarteirinhaComPlano[]>([]);
    const [carteirinhasComPlano, setCarteirinhasComPlano] = useState<CarteirinhaComPlano[]>([]);
    const [menuOpenCarteirinha, setMenuOpenCarteirinha] = useState(false);

    const debouncedCarteirinha = useDebounce(searchCarteirinha, 500);
    const debouncedPaciente = useDebounce(searchPaciente, 500);
    const debouncedProcedimento = useDebounce(searchProcedimento, 500);

    const { data: carteirinhasResponse, isLoading: isLoadingCarteirinhas } = useCarteirinhas(1, 10, debouncedCarteirinha);
    const { data: pacientesResponse, isLoading: isLoadingPacientes } = usePacientes(1, 10, debouncedPaciente);
    const { data: procedimentosResponse, isLoading: isLoadingProcedimentos } = useProcedimentos(1, 10, debouncedProcedimento);

    const form = useForm<GuiaFormData>({
        resolver: zodResolver(guiaSchema),
        defaultValues: {
            carteirinha_id: initialData?.carteirinha_id || "",
            paciente_id: initialData?.paciente_id || "",
            procedimento_id: initialData?.procedimento_id || "",
            numero_guia: initialData?.numero_guia || "",
            tipo: initialData?.tipo || "consulta",
            status: initialData?.status || "rascunho",
            data_solicitacao: initialData?.data_solicitacao?.split('T')[0] || new Date().toISOString().split('T')[0],
            quantidade_solicitada: initialData?.quantidade_solicitada || 1,
            quantidade_autorizada: initialData?.quantidade_autorizada ?? undefined,
            quantidade_executada: initialData?.quantidade_executada ?? undefined,
            motivo_negacao: initialData?.motivo_negacao || "",
            observacoes: initialData?.observacoes || "",
            dados_autorizacao: {
                autorizador: initialData?.dados_autorizacao?.autorizador || "",
                codigo_autorizacao: initialData?.dados_autorizacao?.codigo_autorizacao || "",
                data_autorizacao: initialData?.dados_autorizacao?.data_autorizacao?.split('T')[0] || "",
            },
        },
    });

    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (data: GuiaFormData) => {
        try {
            // Notifica o componente pai que o envio começou
            if (onSubmit) {
                onSubmit();
            }
            
            setIsSubmitting(true);
            
            // Log dos dados antes de formatar (para diagnóstico)
            // console.log("Dados do formulário antes de formatar:", data);
    
            // Formata as datas para o formato ISO com validação mais robusta
            const formattedData: GuiaFormData = {
                ...data,
                data_solicitacao: data.data_solicitacao || new Date().toISOString().split('T')[0],
                quantidade_solicitada: data.quantidade_solicitada || 1,
                // Valores opcionais com verificação segura
                quantidade_autorizada: data.quantidade_autorizada || undefined,
                quantidade_executada: data.quantidade_executada || undefined,
                motivo_negacao: data.motivo_negacao || undefined,
                observacoes: data.observacoes || undefined,
                dados_autorizacao: data.dados_autorizacao ? {
                    autorizador: data.dados_autorizacao.autorizador || "",
                    codigo_autorizacao: data.dados_autorizacao.codigo_autorizacao || "",
                    data_autorizacao: data.dados_autorizacao.data_autorizacao || ""
                } : undefined
            };
    
            // Log dos dados formatados (para diagnóstico)
            // console.log("Dados formatados para envio:", formattedData);
    
            let response;
            if (initialData?.id) {
                // Edição
                // console.log("Atualizando guia existente:", initialData.id);
                response = await guiaService.atualizar(initialData.id, formattedData);
                // console.log("Resposta da atualização:", response);
                
                if (response.success) {
                    toast.success('Guia atualizada com sucesso!');
                    if (onSuccess) {
                        onSuccess();
                    }
                } else {
                    toast.error('Erro ao atualizar guia: ' + (response.message || 'Erro desconhecido'));
                }
            } else {
                // Criação
                // console.log("Criando nova guia");
                response = await guiaService.criar(formattedData);
                // console.log("Resposta da criação:", response);
                
                if (response.success) {
                    toast.success('Guia criada com sucesso!');
                    if (onSuccess) {
                        onSuccess();
                    }
                    form.reset();
                } else {
                    toast.error('Erro ao criar guia: ' + (response.message || 'Erro desconhecido'));
                }
            }
        } catch (error) {
            console.error('Erro ao salvar guia:', error);
            // Mostrar detalhes do erro se disponíveis
            const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
            toast.error(`${initialData?.id ? 'Erro ao atualizar' : 'Erro ao criar'} guia: ${errorMessage}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    const status = form.watch("status");
    const showAutorizacao = status === "autorizada";
    const showNegacao = status === "negada";

    const handlePacienteSearch = async (searchTerm: string) => {
        try {
            const response = await pacienteService.buscarPorTermo(searchTerm, {
                fields: "*" // Garantir que todos os campos sejam retornados
            })
            return response.items || []
        } catch (error) {
            console.error('Erro na busca de pacientes:', error)
            return []
        }
    };

    const handleCarteirinhaSearch = async (query: string): Promise<CarteirinhaComPlano[]> => {
        // Se não tiver paciente selecionado, retorna array vazio
        if (!selectedPaciente) return [];

        // Se tiver query, filtra as carteirinhas
        if (query) {
            return carteirinhasComPlano.filter(carteirinha =>
                carteirinha.numero_carteirinha.toLowerCase().includes(query.toLowerCase()) ||
                (carteirinha.plano_nome || '').toLowerCase().includes(query.toLowerCase())
            );
        }

        // Se não tiver query, retorna todas as carteirinhas
        return carteirinhasComPlano;
    };

    const handleCarteirinhaSelect = async (carteirinha: CarteirinhaComPlano | null) => {
        setSelectedCarteirinha(carteirinha);
        if (carteirinha) {
            form.setValue('carteirinha_id', carteirinha.id);
        } else {
            form.setValue('carteirinha_id', '');
        }
    };

    const handleProcedimentoSearch = async (searchTerm: string) => {
        try {
            // Se o termo estiver vazio, retorna todos os procedimentos
            if (!searchTerm) {
                const response = await procedimentoService.listar(1, 100);
                return response.items || [];
            }
            const response = await procedimentoService.listar(1, 10, searchTerm);
            return response.items || [];
        } catch (error) {
            console.error('Erro na busca de procedimentos:', error);
            return [];
        }
    };

    const handlePacienteSelect = async (paciente: Paciente | null) => {
        setSelectedPaciente(paciente);
        form.setValue("paciente_id", paciente?.id || "", { shouldValidate: true });

        // Se não tiver paciente selecionado, limpa a carteirinha também
        if (!paciente) {
            setSelectedCarteirinha(null);
            form.setValue("carteirinha_id", "", { shouldValidate: true });
            setCarteirinhasDisponiveis([]);
            setCarteirinhasComPlano([]);
            return;
        }

        // Carregar carteirinhas do paciente
        try {
            const response = await carteirinhaService.listarPorPaciente(paciente.id);
            if (response.success && response.data && response.data.length > 0) {
                // Atualiza o estado local das carteirinhas disponíveis
                setCarteirinhasDisponiveis(response.data);

                // Carrega os dados dos planos de saúde
                await carregarCarteirinhasComPlano(response.data);
                
                // Abre automaticamente o dropdown das carteirinhas
                setMenuOpenCarteirinha(true);
            } else {
                toast.warning('Paciente não possui carteirinhas cadastradas');
                setSelectedCarteirinha(null);
                form.setValue("carteirinha_id", "", { shouldValidate: true });
                setCarteirinhasDisponiveis([]);
                setCarteirinhasComPlano([]);
            }
        } catch (error) {
            console.error('Erro ao carregar carteirinhas do paciente:', error);
            toast.error('Erro ao carregar carteirinhas do paciente');
            setCarteirinhasDisponiveis([]);
            setCarteirinhasComPlano([]);
        }
    };

    const carregarCarteirinhasComPlano = async (carteirinhas: Carteirinha[]) => {
        // Obter IDs únicos de plano
        const uniquePlanIds = Array.from(new Set(carteirinhas.map(c => c.plano_saude_id)));

        // Buscar cada plano uma única vez e mapear pelo seu ID, tipando planDataMap explicitamente
        const planDataMap: Record<string, string | undefined> = {};
        await Promise.all(uniquePlanIds.map(async (planId) => {
            try {
                const response = await planoSaudeService.obter(planId);
                planDataMap[planId] = response.success && response.data ? response.data.nome : undefined;
            } catch (error) {
                console.error('Erro ao carregar plano de saúde para ID', planId, error);
                planDataMap[planId] = undefined;
            }
        }));

        // Atualizar cada carteirinha com o nome do plano
        const carteirinhasAtualizadas: CarteirinhaComPlano[] = carteirinhas.map(carteirinha => ({
            ...carteirinha,
            plano_nome: planDataMap[carteirinha.plano_saude_id]
        }));

        setCarteirinhasComPlano(carteirinhasAtualizadas);
    };

    const handleProcedimentoSelect = (procedimento: Procedimento | null) => {
        setSelectedProcedimento(procedimento);
        form.setValue("procedimento_id", procedimento?.id || "", { shouldValidate: true });
    };

    // Efeito para fechar o menu de carteirinhas automaticamente após um tempo
    useEffect(() => {
        if (menuOpenCarteirinha) {
            const timer = setTimeout(() => {
                setMenuOpenCarteirinha(false);
            }, 5000); // Fecha após 5 segundos
            
            return () => clearTimeout(timer);
        }
    }, [menuOpenCarteirinha]);

    useEffect(() => {
        const loadInitialValues = async () => {
            const carteirinhaId = form.getValues('carteirinha_id');
            const pacienteId = form.getValues('paciente_id');
            const procedimentoId = form.getValues('procedimento_id');

            try {
                // Primeiro carrega o paciente
                if (pacienteId) {
                    const pacienteResponse = await pacienteService.obter(pacienteId, "id,nome,cpf");
                    if (pacienteResponse.success && pacienteResponse.data) {
                        setSelectedPaciente(pacienteResponse.data);

                        // Depois carrega as carteirinhas do paciente
                        const carteirinhasResponse = await carteirinhaService.listarPorPaciente(pacienteId);
                        if (carteirinhasResponse.success && carteirinhasResponse.data) {
                            // Atualiza o estado local das carteirinhas disponíveis
                            setCarteirinhasDisponiveis(carteirinhasResponse.data);

                            // Carrega os dados dos planos de saúde
                            await carregarCarteirinhasComPlano(carteirinhasResponse.data);
                            
                            // Se houver carteirinha específica, seleciona
                            if (carteirinhaId) {
                                const carteirinha = carteirinhasResponse.data.find(c => c.id === carteirinhaId);
                                if (carteirinha) {
                                    setSelectedCarteirinha(carteirinha);
                                }
                            }
                        }
                    }
                }

                // Carrega o procedimento
                if (procedimentoId) {
                    const procedimentoResponse = await procedimentoService.obterPorId(procedimentoId);
                    if (procedimentoResponse.success && procedimentoResponse.data) {
                        setSelectedProcedimento(procedimentoResponse.data);
                    }
                }
            } catch (error) {
                console.error('Erro ao carregar dados iniciais:', error);
                toast.error('Erro ao carregar dados iniciais');
            }
        };

        if (initialData) {
            loadInitialValues();
        }
    }, [form, initialData]);

    useEffect((): void => {
        if (selectedPaciente) {
            handleCarteirinhaSearch("");
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedPaciente]);

    return (
        <Form {...form}>
            <form id={id} onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4 py-4 w-full max-w-4xl mx-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                        control={form.control}
                        name="paciente_id"
                        render={({ field }) => (
                            <ComboboxField
                                name="paciente_id"
                                label="Paciente"
                                onSearch={handlePacienteSearch}
                                onSelect={handlePacienteSelect}
                                getOptionLabel={(paciente) => `${paciente.nome} - ${paciente.cpf || ''}`}
                                getOptionValue={(paciente) => paciente.id}
                                disabled={isLoadingPacientes}
                                value={selectedPaciente}
                                isClearable={true}
                            />
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="carteirinha_id"
                        render={({ field }) => (
                            <ComboboxField<CarteirinhaComPlano>
                                key={selectedPaciente ? `carteirinha-${selectedPaciente.id}` : 'carteirinha-empty'}
                                name={field.name}
                                label="Carteirinha"
                                onSearch={handleCarteirinhaSearch}
                                onSelect={handleCarteirinhaSelect}
                                getOptionLabel={(carteirinha) =>
                                    `${carteirinha.numero_carteirinha} - ${carteirinha.plano_nome || 'Sem plano'}`
                                }
                                getOptionValue={(carteirinha) => carteirinha.id}
                                disabled={disabled || !selectedPaciente}
                                placeholder="Selecione uma carteirinha"
                                value={selectedCarteirinha}
                                showAllOptions={true}
                                isClearable={true}
                                menuIsOpen={menuOpenCarteirinha}
                                onFocus={() => setMenuOpenCarteirinha(true)}
                                onBlur={() => {
                                    // Pequeno atraso para permitir a seleção antes de fechar
                                    setTimeout(() => setMenuOpenCarteirinha(false), 200);
                                }}
                                defaultOptions={carteirinhasComPlano}
                            />
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="procedimento_id"
                        render={({ field }) => (
                            <ComboboxField
                                name="procedimento_id"
                                label="Procedimento"
                                onSearch={handleProcedimentoSearch}
                                onSelect={handleProcedimentoSelect}
                                getOptionLabel={(procedimento) => `${procedimento.codigo} - ${procedimento.nome}`}
                                getOptionValue={(procedimento) => procedimento.id}
                                disabled={isLoadingProcedimentos}
                                value={selectedProcedimento}
                                showAllOptions={true}
                                isClearable={true}
                            />
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="numero_guia"
                        render={({ field }) => (
                            <FormItem className="form-item">
                                <FormLabel>Número da Guia</FormLabel>
                                <FormControl className="form-control">
                                    <Input
                                        placeholder="Digite o número da guia"
                                        {...field}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="tipo"
                        render={({ field }) => (
                            <FormItem className="form-item">
                                <FormLabel>Tipo</FormLabel>
                                <FormControl className="form-control">
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecione o tipo" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="consulta">Consulta</SelectItem>
                                            <SelectItem value="exame">Exame</SelectItem>
                                            <SelectItem value="procedimento">Procedimento</SelectItem>
                                            <SelectItem value="internacao">Internação</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="status"
                        render={({ field }) => (
                            <FormItem className="form-item">
                                <FormLabel>Status</FormLabel>
                                <FormControl className="form-control">
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecione o status" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="rascunho">Rascunho</SelectItem>
                                            <SelectItem value="pendente">Pendente</SelectItem>
                                            <SelectItem value="autorizada">Autorizada</SelectItem>
                                            <SelectItem value="negada">Negada</SelectItem>
                                            <SelectItem value="executada">Executada</SelectItem>
                                            <SelectItem value="cancelada">Cancelada</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="data_solicitacao"
                        render={({ field }) => (
                            <FormItem className="form-item">
                                <FormLabel>Data de Solicitação</FormLabel>
                                <FormControl className="form-control">
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="quantidade_solicitada"
                        render={({ field }) => (
                            <FormItem className="form-item">
                                <FormLabel>Quantidade Solicitada</FormLabel>
                                <FormControl className="form-control">
                                    <Input
                                        type="number"
                                        {...field}
                                        value={field.value ?? ""}
                                        onChange={e => field.onChange(Number(e.target.value) || undefined)}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="quantidade_executada"
                        render={({ field }) => (
                            <FormItem className="form-item">
                                <FormLabel>Quantidade Executada</FormLabel>
                                <FormControl className="form-control">
                                    <Input
                                        type="number"
                                        {...field}
                                        value={field.value ?? ""}
                                        onChange={e => field.onChange(Number(e.target.value) || undefined)}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    {showAutorizacao && (
                        <>
                            <FormField
                                control={form.control}
                                name="quantidade_autorizada"
                                render={({ field }) => (
                                    <FormItem className="form-item">
                                        <FormLabel>Quantidade Autorizada</FormLabel>
                                        <FormControl className="form-control">
                                            <Input
                                                type="number"
                                                {...field}
                                                value={field.value ?? ""}
                                                onChange={e => field.onChange(Number(e.target.value) || undefined)}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="dados_autorizacao.autorizador"
                                render={({ field }) => (
                                    <FormItem className="form-item">
                                        <FormLabel>Autorizador</FormLabel>
                                        <FormControl className="form-control">
                                            <Input {...field} value={field.value ?? ""} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="dados_autorizacao.codigo_autorizacao"
                                render={({ field }) => (
                                    <FormItem className="form-item">
                                        <FormLabel>Código de Autorização</FormLabel>
                                        <FormControl className="form-control">
                                            <Input {...field} value={field.value ?? ""} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="dados_autorizacao.data_autorizacao"
                                render={({ field }) => (
                                    <FormItem className="form-item">
                                        <FormLabel>Data de Autorização</FormLabel>
                                        <FormControl className="form-control">
                                            <Input type="date" {...field} value={field.value ?? ""} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </>
                    )}

                    {showNegacao && (
                        <FormField
                            control={form.control}
                            name="motivo_negacao"
                            render={({ field }) => (
                                <FormItem className="form-item col-span-2">
                                    <FormLabel>Motivo da Negação</FormLabel>
                                    <FormControl className="form-control">
                                        <Textarea {...field} value={field.value ?? ""} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    )}

                    <FormField
                        control={form.control}
                        name="observacoes"
                        render={({ field }) => (
                            <FormItem className="form-item col-span-2 mb-8">
                                <FormLabel>Observações</FormLabel>
                                <FormControl className="form-control">
                                    <Textarea {...field} value={field.value ?? ""} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>
            </form>
        </Form>
    );
}