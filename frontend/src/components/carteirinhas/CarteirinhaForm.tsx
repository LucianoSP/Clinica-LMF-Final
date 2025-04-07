import { useForm } from "react-hook-form";
import { z } from "zod";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Carteirinha, CarteirinhaFormData } from "@/types/carteirinha";
import { usePacientes } from "@/hooks/usePacientes";
import { usePlanosSaude } from "@/hooks/usePlanosSaude";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { pacienteService } from "@/services/pacienteService";
import { Paciente } from "@/types/paciente";

const carteirinhaSchema = z.object({
  paciente_id: z.string().uuid("ID do paciente inválido"),
  plano_saude_id: z.string().uuid("ID do plano de saúde inválido"),
  numero_carteirinha: z.string().min(1, "Número da carteirinha é obrigatório"),
  data_validade: z.string().optional(),
  status: z.enum(["ativa", "inativa", "suspensa", "vencida"]),
  motivo_inativacao: z.string().optional().nullable(),
});

const statusOptions = [
  { value: 'ativa', label: 'Ativa' },
  { value: 'inativa', label: 'Inativa' },
  { value: 'suspensa', label: 'Suspensa' },
  { value: 'vencida', label: 'Vencida' },
] as const;

export interface CarteirinhaFormProps {
  carteirinha?: Carteirinha;
  onSubmit: (data: CarteirinhaFormData) => Promise<void>;
  onCancel: () => void;
  id?: string;
}

export function CarteirinhaForm({ carteirinha, onSubmit, onCancel, id }: CarteirinhaFormProps) {
  const isEditing = !!carteirinha?.id;

  const form = useForm<CarteirinhaFormData>({
    resolver: zodResolver(carteirinhaSchema),
    defaultValues: {
      paciente_id: carteirinha?.paciente_id || "",
      plano_saude_id: carteirinha?.plano_saude_id || "",
      numero_carteirinha: carteirinha?.numero_carteirinha || "",
      data_validade: carteirinha?.data_validade || "",
      status: carteirinha?.status || "ativa",
      motivo_inativacao: carteirinha?.motivo_inativacao || "",
    },
  });

  // Só carregamos a lista de pacientes se não estivermos editando
  const { data: pacientesData } = useQuery({
    queryKey: ["pacientes", 1, 100, "", "nome", "asc"],
    queryFn: () => pacienteService.buscarPorTermo("", {
      page: 1,
      limit: 100,
      order_column: "nome",
      order_direction: "asc",
      fields: "*" // Garantir que todos os campos sejam retornados
    }),
    enabled: !isEditing, // Só executa a consulta se não estiver editando
  });

  const { data: planosSaudeData } = usePlanosSaude(1, 100);

  const handleSubmit = async (data: CarteirinhaFormData) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Erro ao salvar carteirinha:', error);
    }
  };

  return (
    <Form {...form}>
      <form id={id} onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4 py-4">
        <FormField
          control={form.control}
          name="paciente_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Paciente</FormLabel>
              {isEditing ? (
                // Se estiver editando, mostra apenas o nome do paciente em um campo não editável
                <FormControl>
                  <Input 
                    value={carteirinha.paciente_nome || "Paciente não identificado"} 
                    disabled 
                    className="bg-muted"
                  />
                </FormControl>
              ) : (
                // Se estiver criando, mostra o select box com todos os pacientes
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um paciente" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {pacientesData?.items.map((paciente: Paciente) => (
                      <SelectItem key={paciente.id} value={paciente.id}>
                        {paciente.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="plano_saude_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plano de Saúde</FormLabel>
              {isEditing ? (
                // Se estiver editando, mostra apenas o nome do plano em um campo não editável
                <FormControl>
                  <Input 
                    value={carteirinha.plano_saude_nome || "Plano não identificado"} 
                    disabled 
                    className="bg-muted"
                  />
                </FormControl>
              ) : (
                // Se estiver criando, mostra o select box com todos os planos
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um plano de saúde" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {planosSaudeData?.items.map((plano) => (
                      <SelectItem key={plano.id} value={plano.id}>
                        {plano.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="numero_carteirinha"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Número da Carteirinha</FormLabel>
              <FormControl>
                <Input {...field} />
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

        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
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

        {form.watch("status") !== "ativa" && (
          <FormField
            control={form.control}
            name="motivo_inativacao"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Motivo da Inativação</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}
      </form>
    </Form>
  );
}
