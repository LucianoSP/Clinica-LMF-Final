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
import { Paciente } from "@/types/paciente";
import { MaskedInput } from '@/components/ui/masked-input';
import { cn } from "@/lib/utils";
import { supabase } from "@/lib/supabase";
import { toast } from "sonner";
import { phoneMask, cpfMask } from '@/utils/masks';
import { useState } from "react";

const pacienteSchema = z.object({
  nome: z.string().min(2, "Nome deve ter no mínimo 2 caracteres"),
  id_origem: z.string().optional().or(z.literal("")),
  nome_responsavel: z.string().min(2, "Nome do responsável deve ter no mínimo 2 caracteres").optional().or(z.literal("")),
  nome_pai: z.string().optional().or(z.literal("")),
  nome_mae: z.string().optional().or(z.literal("")),
  data_nascimento: z.string().optional(),
  cpf: z.string()
    .regex(/^\d{3}\.\d{3}\.\d{3}-\d{2}$/, "CPF deve estar no formato 111.111.111-11")
    .optional()
    .or(z.literal("")),
  rg: z.string().optional().or(z.literal("")),
  sexo: z.string().optional().or(z.literal("")),
  telefone: z.string()
    .min(14, "Telefone inválido")
    .max(15, "Telefone inválido")
    .regex(/^\(\d{2}\) \d{4,5}-\d{4}$/, "Telefone inválido")
    .optional()
    .or(z.literal("")),
  email: z.string().email("Email inválido").optional().or(z.literal("")),
  cep: z.string().optional().or(z.literal("")),
  endereco: z.string().optional().or(z.literal("")),
  numero: z.number().nullable(),
  complemento: z.string().optional().or(z.literal("")),
  bairro: z.string().optional().or(z.literal("")),
  cidade: z.string().optional().or(z.literal("")),
  estado: z.string().optional().or(z.literal("")),
  observacoes: z.string().optional(),
  cpf_responsavel: z.string()
    .regex(/^\d{3}\.\d{3}\.\d{3}-\d{2}$/, "CPF do responsável deve estar no formato 111.111.111-11")
    .optional()
    .or(z.literal("")),
});

export type PacienteFormData = z.infer<typeof pacienteSchema>;

export interface PacienteFormProps {
  paciente?: Paciente;
  onSubmit: (data: PacienteFormData) => Promise<void>;
  onCancel: () => void;
  id?: string;
}

export function PacienteForm({ paciente, onSubmit, onCancel, id }: PacienteFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const form = useForm<PacienteFormData>({
    resolver: zodResolver(pacienteSchema),
    defaultValues: {
      nome: paciente?.nome || "",
      id_origem: paciente?.id_origem || "",
      nome_responsavel: paciente?.nome_responsavel || "",
      nome_pai: paciente?.nome_pai || "",
      nome_mae: paciente?.nome_mae || "",
      data_nascimento: paciente?.data_nascimento || "",
      cpf: paciente?.cpf || "",
      rg: paciente?.rg || "",
      sexo: paciente?.sexo || "",
      telefone: paciente?.telefone || "",
      email: paciente?.email || "",
      cep: paciente?.cep || "",
      endereco: paciente?.endereco || "",
      numero: paciente?.numero ?? null,
      complemento: paciente?.complemento || "",
      bairro: paciente?.bairro || "",
      cidade: paciente?.cidade || "",
      estado: paciente?.estado || "",
      observacoes: paciente?.observacoes || "",
      cpf_responsavel: paciente?.cpf_responsavel || "",
    },
  });

  const handleSubmit = async (data: PacienteFormData) => {
    if (isSubmitting) {
      console.log("PacienteForm.handleSubmit - Já está em processo de submissão, ignorando");
      return;
    }
    
    console.log("PacienteForm.handleSubmit - Formulário submetido com dados:", data);
    setIsSubmitting(true);
    try {
      console.log("PacienteForm.handleSubmit - Chamando onSubmit com dados:", data);
      await onSubmit(data);
      console.log("PacienteForm.handleSubmit - onSubmit concluído com sucesso");
    } catch (error) {
      console.error('PacienteForm.handleSubmit - Erro no submit:', error);
      toast.error('Erro ao salvar paciente');
    } finally {
      console.log("PacienteForm.handleSubmit - Finalizando processo de submissão");
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form id={id} onSubmit={form.handleSubmit((data) => {
        console.log("PacienteForm - Formulário válido, dados:", data);
        handleSubmit(data);
      })} className="space-y-4 py-4">
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="id_origem"
            render={({ field }) => (
              <FormItem>
                <FormLabel>ID Origem</FormLabel>
                <FormControl>
                  <Input 
                    {...field} 
                    placeholder="ID do sistema de origem (opcional)"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="nome_responsavel"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome do Responsável</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormField
            control={form.control}
            name="data_nascimento"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Data de Nascimento</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="cpf"
            render={({ field }) => (
              <FormItem>
                <FormLabel>CPF</FormLabel>
                <FormControl>
                  <MaskedInput
                    {...field}
                    mask={cpfMask}
                    placeholder="111.111.111-11"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="telefone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Telefone</FormLabel>
                <FormControl>
                  <MaskedInput
                    {...field}
                    mask={phoneMask}
                    placeholder="(11) 99999-9999"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" {...field} />
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
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="nome_pai"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Nome do Pai</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="nome_mae"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Nome da Mãe</FormLabel>
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
            name="rg"
            render={({ field }) => (
              <FormItem>
                <FormLabel>RG</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="sexo"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Sexo</FormLabel>
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
          name="cep"
          render={({ field }) => (
            <FormItem>
              <FormLabel>CEP</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-3 gap-4">
          <FormField
            control={form.control}
            name="endereco"
            render={({ field }) => (
              <FormItem className="col-span-2">
                <FormLabel>Endereço</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="numero"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Número</FormLabel>
                <FormControl>
                  <Input 
                    type="number" 
                    {...field} 
                    onChange={e => {
                      const value = e.target.value === '' ? 0 : parseInt(e.target.value, 10);
                      field.onChange(value);
                    }}
                    value={field.value || ''}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="complemento"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Complemento</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="bairro"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Bairro</FormLabel>
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
            name="cidade"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Cidade</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="estado"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Estado</FormLabel>
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
          name="cpf_responsavel"
          render={({ field }) => (
            <FormItem>
              <FormLabel>CPF do Responsável</FormLabel>
              <FormControl>
                <MaskedInput
                  {...field}
                  mask={cpfMask}
                  placeholder="111.111.111-11"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
