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
import { PlanoSaude } from "@/types/plano_saude";
import { MaskedInput } from '@/components/ui/masked-input';
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import { phoneMask } from '@/utils/masks';

const planoSaudeSchema = z.object({
  codigo_operadora: z.string().max(20, "Código da operadora deve ter no máximo 20 caracteres").optional().or(z.literal("")),
  registro_ans: z.string().max(20, "Registro ANS deve ter no máximo 20 caracteres").optional().or(z.literal("")),
  nome: z.string().min(2, "Nome deve ter no mínimo 2 caracteres"),
  tipo_plano: z.string().max(50, "Tipo do plano deve ter no máximo 50 caracteres").optional().or(z.literal("")),
  abrangencia: z.string().max(50, "Abrangência deve ter no máximo 50 caracteres").optional().or(z.literal("")),
  observacoes: z.string().optional().or(z.literal("")),
  ativo: z.boolean().default(true),
  dados_contrato: z.record(z.any()).optional().default({}),
});

export type PlanoSaudeFormData = z.infer<typeof planoSaudeSchema>;

export interface PlanoSaudeFormProps {
  plano_saude?: PlanoSaude;
  onSubmit: (data: PlanoSaudeFormData) => Promise<void>;
  onCancel: () => void;
  onSuccess?: () => void;
  id?: string;
}

export function PlanoSaudeForm({ plano_saude, onSubmit, onCancel, onSuccess, id }: PlanoSaudeFormProps) {
  const form = useForm<PlanoSaudeFormData>({
    resolver: zodResolver(planoSaudeSchema),
    defaultValues: {
      codigo_operadora: plano_saude?.codigo_operadora || "",
      registro_ans: plano_saude?.registro_ans || "",
      nome: plano_saude?.nome || "",
      tipo_plano: plano_saude?.tipo_plano || "",
      abrangencia: plano_saude?.abrangencia || "",
      observacoes: plano_saude?.observacoes || "",
      ativo: plano_saude?.ativo ?? true,
      dados_contrato: plano_saude?.dados_contrato || {},
    },
  });

  const handleSubmit = async (data: PlanoSaudeFormData) => {
    try {
      await onSubmit(data);
      // onSuccess?.();
      // toast.success(plano_saude ? "Plano atualizado com sucesso" : "Plano criado com sucesso");
    } catch (error) {
      console.error('Erro ao salvar plano de saúde:', error);
      toast.error('Erro ao salvar plano de saúde');
    }
  };

  return (
    <Form {...form}>
      <form id={id} onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4 py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="codigo_operadora"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Código da Operadora</FormLabel>
                <FormControl>
                  <Input {...field} maxLength={20} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="registro_ans"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Registro ANS</FormLabel>
                <FormControl>
                  <Input {...field} maxLength={20} />
                </FormControl>
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
              <FormLabel>Nome do Plano</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="tipo_plano"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Tipo do Plano</FormLabel>
                <FormControl>
                  <Input {...field} maxLength={50} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="abrangencia"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Abrangência</FormLabel>
                <FormControl>
                  <Input {...field} maxLength={50} />
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
                <Textarea 
                  {...field}
                  className="min-h-[100px]"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="ativo"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <FormLabel className="text-base">Status do Plano</FormLabel>
                <div className="text-sm text-muted-foreground">
                  Este plano está ativo para uso no sistema?
                </div>
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
