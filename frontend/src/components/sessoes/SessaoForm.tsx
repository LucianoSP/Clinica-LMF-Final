import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Sessao, SessaoFormData, StatusSessao, TipoAtendimento } from "@/types/sessao";

interface SessaoFormProps {
    onSubmit: (data: SessaoFormData) => void;
    sessao?: Sessao;
    loading?: boolean;
}

export function SessaoForm({ onSubmit, sessao, loading }: SessaoFormProps) {
    const { register, handleSubmit, formState: { errors } } = useForm<SessaoFormData>({
        defaultValues: sessao || {
            status: 'agendada',
            tipo_atendimento: 'presencial'
        }
    });

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium mb-1">Data da Sessão</label>
                    <Input
                        type="date"
                        {...register("data_sessao", { required: "Data é obrigatória" })}
                    />
                    {errors.data_sessao && (
                        <span className="text-red-500 text-sm">{errors.data_sessao.message}</span>
                    )}
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">Tipo de Atendimento</label>
                    <Select
                        {...register("tipo_atendimento", { required: "Tipo é obrigatório" })}
                    >
                        <option value="presencial">Presencial</option>
                        <option value="teleconsulta">Teleconsulta</option>
                    </Select>
                    {errors.tipo_atendimento && (
                        <span className="text-red-500 text-sm">{errors.tipo_atendimento.message}</span>
                    )}
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">Hora Início</label>
                    <Input
                        type="time"
                        {...register("hora_inicio")}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">Hora Fim</label>
                    <Input
                        type="time"
                        {...register("hora_fim")}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-1">Status</label>
                    <Select
                        {...register("status")}
                    >
                        <option value="agendada">Agendada</option>
                        <option value="realizada">Realizada</option>
                        <option value="cancelada">Cancelada</option>
                        <option value="faltou">Faltou</option>
                    </Select>
                </div>
            </div>

            <div>
                <label className="block text-sm font-medium mb-1">Evolução</label>
                <Textarea
                    {...register("evolucao")}
                    rows={4}
                />
            </div>

            <div>
                <label className="block text-sm font-medium mb-1">Observações</label>
                <Textarea
                    {...register("observacoes")}
                    rows={2}
                />
            </div>

            <div className="flex justify-end space-x-2">
                <Button
                    type="submit"
                    disabled={loading}
                >
                    {loading ? 'Salvando...' : 'Salvar'}
                </Button>
            </div>
        </form>
    );
} 