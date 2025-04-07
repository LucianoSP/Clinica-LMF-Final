import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PacienteForm, PacienteFormData } from "./PacienteForm";
import { Paciente } from "@/types/paciente";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { 
  pacienteService 
} from "@/services/pacienteService";
import { getCurrentUserId } from '@/services/api';
import { Button } from "@/components/ui/button"; // Import Button component
import { useState } from 'react'; // Import useState hook

interface PacienteModalProps {
  isOpen: boolean;
  onClose: () => void;
  paciente?: Paciente;
}

export function PacienteModal({ isOpen, onClose, paciente }: PacienteModalProps) {
    // const { user } = useAuth();
    // console.log('PacienteModal user', user);
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (formData: PacienteFormData) => {
    try {
        setIsSubmitting(true);
        console.log('PacienteModal.handleSubmit - Iniciando submissão do formulário');
      const userId = await getCurrentUserId();
      console.log('PacienteModal.handleSubmit - Obteve userId:', userId);
      console.log('PacienteModal.handleSubmit - Dados do formulário:', formData);
      
      if (paciente) {
        // Atualização de paciente existente
        console.log('PacienteModal.handleSubmit - Atualizando paciente existente:', paciente.id);
        const dadosAtualizacao = {
          ...formData,
          updated_by: userId
        };
        console.log('PacienteModal.handleSubmit - Dados para atualização:', dadosAtualizacao);
        
        const response = await pacienteService.atualizar(paciente.id, dadosAtualizacao);
        
        console.log('PacienteModal.handleSubmit - Resposta da atualização:', response);
        
        if (!response.success) {
          throw new Error(response.message || 'Erro ao atualizar paciente');
        }
        
        toast.success('Paciente atualizado com sucesso');
      } else {
        // Criação de novo paciente
        console.log('PacienteModal.handleSubmit - Criando novo paciente');
        const response = await pacienteService.criar({
          ...formData,
          created_by: userId,
          updated_by: userId
        });
        
        console.log('PacienteModal.handleSubmit - Resposta da criação:', response);
        
        if (!response.success) {
          // console.log('response', response); // success: false, message: "Network Error"
          throw new Error(response.message || 'Erro ao criar paciente-x');
        }
        
        toast.success('Paciente criado com sucesso');
      }

      await queryClient.invalidateQueries({ queryKey: ['pacientes'] });
      onClose();
    } catch (error: any) {
      console.error('PacienteModal.handleSubmit - Erro ao salvar paciente:', error);
      
      // Tratamento específico para erro de autenticação
      if (error.message?.includes('AuthSessionMissingError')) {
        toast.error('Sessão expirada. Por favor, faça login novamente.');
        return;
      }
      
      const acao = paciente ? 'atualizar' : 'criar';
      toast.error(`Erro ao ${acao} paciente. Por favor, tente novamente.`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog 
      open={isOpen} 
      onOpenChange={(open) => {
        // Só permite fechar o modal através dos botões, não por clique externo
        if (open === false) {
          // Não faz nada, impedindo o fechamento automático
          return;
        }
        onClose();
      }}
    >
      <DialogContent 
        className="sm:max-w-[600px] max-h-[90vh] flex flex-col p-0 overflow-hidden"
        onPointerDownOutside={(e) => {
          // Previne o fechamento ao clicar fora
          e.preventDefault();
        }}
        onOpenAutoFocus={(e) => {
          // Previne o foco automático
          e.preventDefault();
        }}
      >
        <DialogHeader className="p-6 pb-2">
          <DialogTitle>
            {paciente ? "Editar Paciente" : "Novo Paciente"}
          </DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-y-auto p-6 pt-2">
          <PacienteForm
            paciente={paciente}
            onSubmit={handleSubmit}
            onCancel={onClose}
            id="paciente-form" // Add id to PacienteForm
          />
        </div>
        <div className="border-t p-4 bg-background">
          <div className="flex justify-end space-x-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose}
            >
              Cancelar
            </Button>
            <Button 
              type="button"
              disabled={isSubmitting}
              onClick={(e) => {
                console.log("Botão Atualizar/Cadastrar clicado diretamente");
                
                // Obter o formulário
                const formElement = document.getElementById("paciente-form") as HTMLFormElement;
                if (formElement) {
                  console.log("Formulário encontrado, submetendo");
                  
                  // Criar e disparar o evento de submit
                  const submitEvent = new Event("submit", { bubbles: true, cancelable: true });
                  formElement.dispatchEvent(submitEvent);
                } else {
                  console.error("Formulário não encontrado");
                }
              }}
            >
              {isSubmitting 
                ? "Processando..." 
                : paciente ? "Atualizar" : "Cadastrar"
              }
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}