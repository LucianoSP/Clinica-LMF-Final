import { useForm, Controller, FormProvider } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
    Select, 
    SelectContent, 
    SelectItem, 
    SelectTrigger, 
    SelectValue 
} from "@/components/ui/select";
import { Ficha, FichaData } from "@/types/ficha";
import { formatDateToISO } from "@/utils/date";
import { useEffect, useState } from "react";
import { ComboboxField } from "@/components/ui/combobox-field";
import { FormField } from "@/components/ui/form";
import { pacienteService } from "@/services/pacienteService";
import { carteirinhaService } from "@/services/carteirinhaService";
import { planoSaudeService } from "@/services/planoSaudeService";
import { guiaService } from "@/services/guiaService";
import { toast } from "sonner";
import { Carteirinha } from "@/types/carteirinha";
import { Guia } from "@/types/guia";

interface CarteirinhaComPlano extends Carteirinha {
    plano_nome?: string;
}

interface FichaFormProps {
    onSubmit: (data: FichaData) => void;
    onCancel?: () => void;
    ficha?: Ficha;
    loading?: boolean;
    id?: string;
}

export function FichaForm({ onSubmit, ficha, loading, onCancel, id }: FichaFormProps) {
    // Log para verificar os valores iniciais da ficha
    // console.log("Valores iniciais da ficha:", ficha);
    
    // Preparar os valores padrão
    const defaultValues = ficha ? {
        ...ficha,
        numero_guia: ficha.numero_guia || "",
        guia_id: ficha.guia_id || "",
        paciente_nome: ficha.paciente_nome || "",
        paciente_carteirinha: ficha.paciente_carteirinha || "",
        data_atendimento: ficha.data_atendimento ? 
            formatDateToISO(ficha.data_atendimento) : 
            formatDateToISO(new Date().toISOString())
    } : {
        status: 'pendente' as const,
        total_sessoes: 1,
        numero_guia: "",
        guia_id: "",
        paciente_nome: "",
        paciente_carteirinha: "",
        data_atendimento: formatDateToISO(new Date().toISOString())
    };

    const methods = useForm<FichaData>({ defaultValues });
    const { register, handleSubmit, control, formState: { errors }, watch, setValue } = methods;

    // Estados locais para manter seleção dos combobox
    const [selectedPaciente, setSelectedPaciente] = useState<any>(null);
    const [selectedCarteirinha, setSelectedCarteirinha] = useState<CarteirinhaComPlano | null>(null);
    const [selectedGuia, setSelectedGuia] = useState<Guia | null>(null);
    const [carteirinhasDisponiveis, setCarteirinhasDisponiveis] = useState<CarteirinhaComPlano[]>([]);
    const [guiasDisponiveis, setGuiasDisponiveis] = useState<Guia[]>([]);
    const [menuOpenCarteirinha, setMenuOpenCarteirinha] = useState(false);
    const [menuOpenGuia, setMenuOpenGuia] = useState(false);

    // Função para buscar guias da carteirinha selecionada
    const handleGuiaSearch = async (term: string) => {
        // console.log("Buscando guias com termo:", term, "Guias disponíveis:", guiasDisponiveis);
        
        // Sempre retornar todas as guias disponíveis se não houver termo de busca
        if (!term || term.trim() === '') {
            return guiasDisponiveis;
        }
        
        // Filtrar as guias pelo termo de busca
        return guiasDisponiveis.filter(guia => 
            guia.numero_guia.toLowerCase().includes(term.toLowerCase())
        );
    };

    // Função para carregar guias do paciente e filtrar pela carteirinha
    const carregarGuias = async (carteirinha: CarteirinhaComPlano) => {
        if (!carteirinha || !selectedPaciente) {
            setGuiasDisponiveis([]);
            return;
        }
        
        try {
            // console.log("Carregando guias para o paciente ID:", selectedPaciente.id);
            // console.log("Carteirinha selecionada:", carteirinha);
            
            // Usar o ID do paciente para buscar todas as guias dele
            const response = await guiaService.listarPorPaciente(selectedPaciente.id);
            
            // console.log("Resposta guias do paciente:", response);
            
            // Verificar se há guias na resposta (items em vez de data)
            if (response.success && response.items && response.items.length > 0) {
                // console.log("Total de guias do paciente:", response.items.length);
                
                // Log de todas as guias e suas carteirinha_id
                // response.items.forEach((guia: Guia, index: number) => {
                //     console.log(`Guia ${index + 1}:`, {
                //         id: guia.id,
                //         numero_guia: guia.numero_guia,
                //         carteirinha_id: guia.carteirinha_id,
                //         status: guia.status
                //     });
                // });
                
                // Tem guias, mas pode ser que nenhuma corresponda à carteirinha
                // console.log("Carteirinha ID para filtrar:", carteirinha.id);
                
                // Filtrar apenas as guias que pertencem à carteirinha selecionada
                const guiasDaCarteirinha = response.items.filter((guia: Guia) => {
                    const matches = guia.carteirinha_id === carteirinha.id;
                    // console.log(`Guia ${guia.numero_guia} match: ${matches} (ID da guia: ${guia.carteirinha_id}, ID da carteirinha: ${carteirinha.id})`);
                    return matches;
                });
                
                // console.log("Guias filtradas para esta carteirinha:", guiasDaCarteirinha);
                
                if (guiasDaCarteirinha.length > 0) {
                    setGuiasDisponiveis(guiasDaCarteirinha);
                } else {
                    // Se não encontrou nenhuma guia para a carteirinha específica,
                    // pode ser que os IDs estejam em formatos diferentes
                    console.warn('Nenhuma guia encontrada para esta carteirinha');
                    toast.warning('Carteirinha não possui guias cadastradas');
                    setGuiasDisponiveis([]);
                }
            } else {
                console.warn('Paciente não possui guias cadastradas');
                toast.warning('Paciente não possui guias cadastradas');
                setGuiasDisponiveis([]);
            }
        } catch (error) {
            console.error('Erro ao carregar guias do paciente:', error);
            toast.error('Erro ao carregar guias');
            setGuiasDisponiveis([]);
        }
    };

    // Função para buscar pacientes - usando o serviço otimizado
    const handlePacienteSearch = async (term: string) => {
        try {
            // Se o termo de busca for vazio, não realiza a busca
            if (!term.trim()) {
                return [];
            }
            
            // console.log("Buscando pacientes com termo:", term);
            const response = await pacienteService.buscarParaCombobox(term);
            // console.log(`Encontrados ${response.data?.length || 0} pacientes para o termo "${term}"`, response.data);
            return response.data || [];
        } catch (error) {
            console.error('Erro na busca de pacientes:', error);
            return [];
        }
    };

    // Função para carregar carteirinhas do paciente com dados do plano
    const carregarCarteirinhasComPlano = async (carteirinhas: Carteirinha[]) => {
        if (!carteirinhas || carteirinhas.length === 0) return [];

        // Obter IDs únicos de plano
        const uniquePlanIds = Array.from(new Set(carteirinhas.map(c => c.plano_saude_id)));
        
        // Buscar cada plano uma única vez e mapear pelo seu ID
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
        
        return carteirinhasAtualizadas;
    };

    // Função para carregar carteirinhas do paciente
    const carregarCarteirinhas = async (pacienteId: string) => {
        if (!pacienteId) {
            setCarteirinhasDisponiveis([]);
            return;
        }
        
        try {
            const response = await carteirinhaService.listarPorPaciente(pacienteId);
            if (response.success && response.data && response.data.length > 0) {
                const carteirinhasComPlano = await carregarCarteirinhasComPlano(response.data);
                setCarteirinhasDisponiveis(carteirinhasComPlano);
                // Não abrir o menu automaticamente
            } else {
                toast.warning('Paciente não possui carteirinhas cadastradas');
                setCarteirinhasDisponiveis([]);
            }
        } catch (error) {
            console.error('Erro ao carregar carteirinhas do paciente:', error);
            toast.error('Erro ao carregar carteirinhas do paciente');
            setCarteirinhasDisponiveis([]);
        }
    };

    // Função para buscar carteirinhas
    const handleCarteirinhaSearch = async (term: string) => {
        // Se tiver termo de busca, filtra as carteirinhas carregadas
        if (term) {
            return carteirinhasDisponiveis.filter(carteirinha =>
                carteirinha.numero_carteirinha.toLowerCase().includes(term.toLowerCase()) || 
                (carteirinha.plano_nome && carteirinha.plano_nome.toLowerCase().includes(term.toLowerCase()))
            );
        }
        
        // Se não tiver termo, retorna todas as carteirinhas carregadas
        return carteirinhasDisponiveis;
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

    // Efeito para fechar o menu de guias automaticamente após um tempo
    useEffect(() => {
        if (menuOpenGuia) {
            const timer = setTimeout(() => {
                setMenuOpenGuia(false);
            }, 5000); // Fecha após 5 segundos
            
            return () => clearTimeout(timer);
        }
    }, [menuOpenGuia]);

    // Monitorar data_atendimento para log
    const watchedDate = watch("data_atendimento");
    useEffect(() => {
        // console.log("Valor atual de data_atendimento:", watchedDate, "tipo:", typeof watchedDate);
    }, [watchedDate]);

    // Monitorar guiasDisponiveis para log
    useEffect(() => {
        // console.log("Guias disponíveis atualizadas:", guiasDisponiveis);
    }, [guiasDisponiveis]);

    // Carregar dados iniciais quando ficha existente é passada para edição
    useEffect(() => {
        const carregarDadosIniciais = async () => {
            if (ficha) {
                // console.log("Carregando dados iniciais da ficha:", ficha);
                try {
                    // Buscar paciente pelo nome ou ID
                    if (ficha.paciente_id || ficha.paciente_nome) {
                        let pacienteEncontrado;
                        
                        // Se tiver ID do paciente, buscar diretamente
                        if (ficha.paciente_id) {
                            try {
                                const pacienteResponse = await pacienteService.obter(ficha.paciente_id, "id,nome,cpf");
                                if (pacienteResponse.success && pacienteResponse.data) {
                                    pacienteEncontrado = pacienteResponse.data;
                                }
                            } catch (error) {
                                console.error('Erro ao buscar paciente por ID:', error);
                            }
                        }
                        
                        // Se não encontrou por ID ou não tinha ID, buscar por nome
                        if (!pacienteEncontrado && ficha.paciente_nome) {
                            const pacientesResponse = await pacienteService.buscarPorTermo(ficha.paciente_nome, {
                                fields: "*" // Garantir que todos os campos sejam retornados
                            });
                            if (pacientesResponse.items && pacientesResponse.items.length > 0) {
                                // Encontrar o paciente que corresponde ao nome exato ou ao ID
                                pacienteEncontrado = pacientesResponse.items.find(
                                    p => p.nome.toLowerCase() === ficha.paciente_nome?.toLowerCase() || 
                                         p.id === ficha.paciente_id
                                ) || pacientesResponse.items[0];
                            }
                        }
                        
                        if (pacienteEncontrado) {
                            // console.log("Paciente encontrado:", pacienteEncontrado);
                            setSelectedPaciente(pacienteEncontrado);
                            setValue("paciente_nome", pacienteEncontrado.nome, { shouldValidate: true });
                            setValue("paciente_id", pacienteEncontrado.id, { shouldValidate: true });
                            
                            // Carregar carteirinhas do paciente
                            if (pacienteEncontrado.id) {
                                const carteirinhasResponse = await carteirinhaService.listarPorPaciente(pacienteEncontrado.id);
                                if (carteirinhasResponse.success && carteirinhasResponse.data && carteirinhasResponse.data.length > 0) {
                                    const carteirinhasComPlano = await carregarCarteirinhasComPlano(carteirinhasResponse.data);
                                    setCarteirinhasDisponiveis(carteirinhasComPlano);
                                    // console.log("Carteirinhas disponíveis:", carteirinhasComPlano);
                                    
                                    // Encontrar a carteirinha pelo ID ou número
                                    let carteirinhaEncontrada;
                                    if (ficha.carteirinha_id) {
                                        carteirinhaEncontrada = carteirinhasComPlano.find(
                                            c => c.id === ficha.carteirinha_id
                                        );
                                    } else if (ficha.paciente_carteirinha) {
                                        carteirinhaEncontrada = carteirinhasComPlano.find(
                                            c => c.numero_carteirinha === ficha.paciente_carteirinha
                                        );
                                    }
                                    
                                    if (carteirinhaEncontrada) {
                                        // console.log("Carteirinha encontrada:", carteirinhaEncontrada);
                                        setSelectedCarteirinha(carteirinhaEncontrada);
                                        setValue("paciente_carteirinha", carteirinhaEncontrada.numero_carteirinha, { shouldValidate: true });
                                        
                                        // Carregar guias da carteirinha
                                        const guiasResponse = await guiaService.listarPorPaciente(pacienteEncontrado.id);
                                        // console.log("Guias do paciente:", guiasResponse);
                                        
                                        if (guiasResponse.success && guiasResponse.items && guiasResponse.items.length > 0) {
                                            // Filtrar guias pela carteirinha
                                            const guiasDaCarteirinha = guiasResponse.items.filter(
                                                (g: Guia) => g.carteirinha_id === carteirinhaEncontrada.id
                                            );
                                            
                                            setGuiasDisponiveis(guiasDaCarteirinha);
                                            // console.log("Guias da carteirinha:", guiasDaCarteirinha);
                                            
                                            // Encontrar a guia pelo ID ou número
                                            let guiaEncontrada;
                                            if (ficha.guia_id) {
                                                guiaEncontrada = guiasDaCarteirinha.find(
                                                    g => g.id === ficha.guia_id
                                                );
                                            } else if (ficha.numero_guia) {
                                                guiaEncontrada = guiasDaCarteirinha.find(
                                                    g => g.numero_guia === ficha.numero_guia
                                                );
                                            }
                                            
                                            if (guiaEncontrada) {
                                                // console.log("Guia encontrada:", guiaEncontrada);
                                                setSelectedGuia(guiaEncontrada);
                                                setValue("numero_guia", guiaEncontrada.numero_guia, { shouldValidate: true });
                                                setValue("guia_id", guiaEncontrada.id, { shouldValidate: true });
                                            } else {
                                                console.warn("Guia não encontrada com número:", ficha.numero_guia);
                                                // Se não encontrou a guia, mas temos o número, podemos criar um objeto temporário
                                                if (ficha.numero_guia) {
                                                    const guiaTemp = {
                                                        id: ficha.guia_id || "",
                                                        numero_guia: ficha.numero_guia,
                                                        carteirinha_id: carteirinhaEncontrada.id
                                                    };
                                                    // console.log("Criando guia temporária:", guiaTemp);
                                                    setSelectedGuia(guiaTemp as any);
                                                    setValue("numero_guia", ficha.numero_guia, { shouldValidate: true });
                                                    if (ficha.guia_id) {
                                                        setValue("guia_id", ficha.guia_id, { shouldValidate: true });
                                                    }
                                                }
                                            }
                                        } else {
                                            console.warn("Nenhuma guia encontrada para o paciente");
                                            // Se não encontrou guias, mas temos o número, podemos criar um objeto temporário
                                            if (ficha.numero_guia) {
                                                const guiaTemp = {
                                                    id: ficha.guia_id || "",
                                                    numero_guia: ficha.numero_guia,
                                                    carteirinha_id: carteirinhaEncontrada.id
                                                };
                                                // console.log("Criando guia temporária:", guiaTemp);
                                                setSelectedGuia(guiaTemp as any);
                                                setValue("numero_guia", ficha.numero_guia, { shouldValidate: true });
                                                if (ficha.guia_id) {
                                                    setValue("guia_id", ficha.guia_id, { shouldValidate: true });
                                                }
                                            }
                                        }
                                    } else {
                                        console.warn("Carteirinha não encontrada com número:", ficha.paciente_carteirinha);
                                    }
                                } else {
                                    console.warn("Nenhuma carteirinha encontrada para o paciente");
                                }
                            }
                        } else {
                            console.warn("Paciente não encontrado com nome:", ficha.paciente_nome);
                        }
                    }
                } catch (error) {
                    console.error('Erro ao carregar dados iniciais:', error);
                    toast.error('Erro ao carregar dados iniciais');
                }
            }
        };
        
        carregarDadosIniciais();
    }, [ficha, setValue]);

    const processForm = (data: FichaData) => {
        const formattedData: FichaData = { ...data, data_atendimento: formatDateToISO(data.data_atendimento) };
        // console.log("Dados formatados antes de enviar:", formattedData);
        onSubmit(formattedData);
    };

    return (
        <FormProvider {...methods}>
        <form id={id} onSubmit={handleSubmit(processForm)} className="space-y-4">
            <div className="space-y-4">
                {/* Combobox para Nome do Paciente */}
                <FormField
                    control={control}
                    name="paciente_nome"
                    render={({ field }) => (
                        <ComboboxField
                            {...field}
                            name="paciente_nome"
                            label="Paciente"
                            onSearch={handlePacienteSearch}
                            onSelect={(option) => {
                                if (option) {
                                    field.onChange(option.nome || ""); // Armazena o nome do paciente
                                    setSelectedPaciente(option); // Armazena o objeto paciente completo
                                    setValue("paciente_id", option.id || "", { shouldValidate: true }); // Armazena o ID separadamente
                                    
                                    // Carregar carteirinhas do paciente sem abrir o dropdown
                                    carregarCarteirinhas(option.id);
                                } else {
                                    field.onChange("");
                                    setSelectedPaciente(null);
                                    setValue("paciente_id", "", { shouldValidate: true });
                                    setCarteirinhasDisponiveis([]);
                                }
                                
                                // Limpar os campos dependentes
                                setValue("paciente_carteirinha", "");
                                setValue("numero_guia", "");
                                setValue("guia_id", "");
                                setSelectedCarteirinha(null);
                                setSelectedGuia(null);
                                setGuiasDisponiveis([]);
                            }}
                            getOptionLabel={(paciente: any) => `${paciente.nome} - ${paciente.cpf || ''}`}
                            getOptionValue={(paciente: any) => paciente.id}
                            isClearable={true}
                            value={selectedPaciente} // Passa o objeto paciente completo
                            minInputLength={1} // Permite buscar com apenas 1 caractere
                            placeholder="Digite o nome do paciente..."
                        />
                    )}
                />
                {errors.paciente_nome && (
                    <span className="text-red-500 text-sm">{errors.paciente_nome.message as string}</span>
                )}

                {/* Combobox para Carteirinha, exibida somente se paciente estiver selecionado */}
                {selectedPaciente && (
                    <FormField
                        control={control}
                        name="paciente_carteirinha"
                        render={({ field }) => (
                            <ComboboxField
                                {...field}
                                name="paciente_carteirinha"
                                label="Carteirinha"
                                onSearch={handleCarteirinhaSearch}
                                onSelect={(option) => {
                                    if (option) {
                                        field.onChange(option.numero_carteirinha || "");
                                        setSelectedCarteirinha(option);
                                        
                                        // Carregar guias para a carteirinha selecionada
                                        carregarGuias(option);
                                    } else {
                                        field.onChange("");
                                        setSelectedCarteirinha(null);
                                        setGuiasDisponiveis([]);
                                    }
                                    
                                    // Limpar o campo dependente
                                    setValue("numero_guia", "");
                                    setValue("guia_id", "");
                                    setSelectedGuia(null);
                                }}
                                getOptionLabel={(carteirinha: any) => {
                                    // Mostra apenas o número da carteirinha se não tiver plano_nome
                                    if (!carteirinha.plano_nome) return carteirinha.numero_carteirinha;
                                    // Mostra número da carteirinha e nome do plano se tiver
                                    return `${carteirinha.numero_carteirinha} - ${carteirinha.plano_nome}`;
                                }}
                                getOptionValue={(carteirinha: any) => carteirinha.id}
                                isClearable={true}
                                value={selectedCarteirinha}
                                showAllOptions={true}
                                menuIsOpen={menuOpenCarteirinha}
                                onFocus={() => setMenuOpenCarteirinha(true)}
                                onBlur={() => {
                                    // Pequeno atraso para permitir a seleção antes de fechar
                                    setTimeout(() => setMenuOpenCarteirinha(false), 200);
                                }}
                                defaultOptions={carteirinhasDisponiveis}
                            />
                        )}
                    />
                )}
                {errors.paciente_carteirinha && (
                    <span className="text-red-500 text-sm">{errors.paciente_carteirinha.message as string}</span>
                )}

                {/* Combobox para Número da Guia, exibida somente se carteirinha estiver selecionada */}
                {selectedCarteirinha && (
                    <FormField
                        control={control}
                        name="numero_guia"
                        render={({ field }) => (
                            <ComboboxField
                                {...field}
                                name="numero_guia"
                                label="Número da Guia"
                                onSearch={handleGuiaSearch}
                                onSelect={(option) => {
                                    if (option) {
                                        field.onChange(option.numero_guia || "");
                                        setSelectedGuia(option);
                                        setValue("guia_id", option.id || "", { shouldValidate: true });
                                        // console.log("Guia selecionada:", option, "Valor definido:", option.numero_guia, "ID:", option.id);
                                    } else {
                                        field.onChange("");
                                        setSelectedGuia(null);
                                        setValue("guia_id", "", { shouldValidate: true });
                                        // console.log("Guia desmarcada");
                                    }
                                }}
                                getOptionLabel={(guia: any) => {
                                    // Mostrar mais informações sobre a guia
                                    const status = guia.status ? ` - ${guia.status.charAt(0).toUpperCase() + guia.status.slice(1)}` : '';
                                    const tipo = guia.tipo ? ` - ${guia.tipo.charAt(0).toUpperCase() + guia.tipo.slice(1)}` : '';
                                    return `${guia.numero_guia}${status}${tipo}`;
                                }}
                                getOptionValue={(guia: any) => guia.id}
                                isClearable={true}
                                value={selectedGuia}
                                showAllOptions={true}
                                menuIsOpen={menuOpenGuia}
                                onFocus={() => {
                                    setMenuOpenGuia(true);
                                    // console.log("Menu de guias aberto, guias disponíveis:", guiasDisponiveis);
                                }}
                                onBlur={() => {
                                    // Pequeno atraso para permitir a seleção antes de fechar
                                    setTimeout(() => setMenuOpenGuia(false), 200);
                                }}
                                defaultOptions={guiasDisponiveis}
                                placeholder={
                                    guiasDisponiveis.length === 0 
                                        ? "Nenhuma guia disponível para esta carteirinha"
                                        : `Selecione uma guia (${guiasDisponiveis.length} disponíveis)`
                                }
                            />
                        )}
                    />
                )}
                {errors.numero_guia && (
                    <span className="text-red-500 text-sm">{errors.numero_guia.message as string}</span>
                )}

                {/* Campo Código da Ficha, exibida somente se guia estiver selecionada */}
                {selectedGuia && (
                    <div className="space-y-2">
                        <label htmlFor="codigo_ficha" className="text-sm font-medium">Código da Ficha</label>
                        <FormField
                            control={control}
                            name="codigo_ficha"
                            render={({ field }) => (
                                <Input id="codigo_ficha" {...field} placeholder="Digite o código da ficha" />
                            )}
                        />
                        {errors.codigo_ficha && (
                            <span className="text-red-500 text-sm">{errors.codigo_ficha.message}</span>
                        )}
                    </div>
                )}

                {/* Campos fixos */}
                <div className="space-y-2">
                    <label htmlFor="data_atendimento" className="text-sm font-medium">Data do Atendimento</label>
                    <Input
                        id="data_atendimento"
                        type="date"
                        {...register("data_atendimento", { 
                            required: "Data é obrigatória",
                            setValueAs: (value) => formatDateToISO(value)
                        })}
                    />
                    {errors.data_atendimento && (
                        <span className="text-red-500 text-sm">{errors.data_atendimento.message}</span>
                    )}
                </div>

                <div className="space-y-2">
                    <label htmlFor="total_sessoes" className="text-sm font-medium">Total de Sessões</label>
                    <Input
                        id="total_sessoes"
                        type="number"
                        min="1"
                        {...register("total_sessoes", {
                            valueAsNumber: true,
                            setValueAs: (value) => Number(value) || 1
                        })}
                    />
                    {errors.total_sessoes && (
                        <span className="text-red-500 text-sm">{errors.total_sessoes.message}</span>
                    )}
                </div>

                <div className="space-y-2">
                    <label htmlFor="status" className="text-sm font-medium">Status</label>
                    <Controller
                        name="status"
                        control={control}
                        render={({ field }) => (
                            <Select 
                                value={field.value} 
                                onValueChange={field.onChange}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Selecione um status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="pendente">Pendente</SelectItem>
                                    <SelectItem value="conferida">Conferida</SelectItem>
                                    <SelectItem value="faturada">Faturada</SelectItem>
                                    <SelectItem value="cancelada">Cancelada</SelectItem>
                                </SelectContent>
                            </Select>
                        )}
                    />
                    {errors.status && (
                        <span className="text-red-500 text-sm">{errors.status.message}</span>
                    )}
                </div>
            </div>
        </form>
        </FormProvider>
    );
}