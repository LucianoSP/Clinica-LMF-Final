import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PlanoSaudeForm, PlanoSaudeFormData } from "./PlanoSaudeForm";
import { PlanoSaude } from "@/types/plano_saude";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { planoSaudeService } from "@/services/planoSaudeService";
import { getCurrentUserId } from '@/services/api';
import { Button } from "@/components/ui/button";
import { useState } from 'react';

interface PlanoSaudeModalProps {
  isOpen: boolean;
  onClose: () => void;
  plano_saude?: PlanoSaude;
  onSuccess?: () => void;
}

export function PlanoSaudeModal({ isOpen, onClose, plano_saude, onSuccess }: PlanoSaudeModalProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (formData: PlanoSaudeFormData) => {
    try {
      setIsSubmitting(true);
      const userId = await getCurrentUserId();

      if (plano_saude) {
        // Atualização de plano existente
        await planoSaudeService.atualizar(plano_saude.id, {
          ...formData,
          updated_by: userId
        });
        toast.success('Plano de saúde atualizado com sucesso');
      } else {
        // Criação de novo plano
        await planoSaudeService.criar({
          ...formData,
          created_by: userId,
          updated_by: userId
        });
        toast.success('Plano de saúde criado com sucesso');
      }

      await queryClient.invalidateQueries({ queryKey: ['planos-saude'] });
      onSuccess?.();
      onClose();
    } catch (error: any) {
      console.error('Erro ao salvar plano de saúde:', error);
      
      if (error.message?.includes('AuthSessionMissingError')) {
        toast.error('Sessão expirada. Por favor, faça login novamente.');
        return;
      }
      
      const acao = plano_saude ? 'atualizar' : 'criar';
      toast.error(`Erro ao ${acao} plano de saúde. Por favor, tente novamente.`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(isOpen) => {
      // Só permite fechar o modal através dos botões
      if (!isOpen) {
        return;
      }
      onClose();
    }}>
      <DialogContent 
        className="sm:max-w-[600px] max-h-[90vh] flex flex-col p-0 overflow-hidden"
        onOpenAutoFocus={(e) => {
          // Previne o foco automático
          e.preventDefault();
        }}
        onEscapeKeyDown={(e) => {
          // Previne o fechamento ao pressionar ESC
          e.preventDefault();
        }}
        onInteractOutside={(e) => {
          // Previne o fechamento ao clicar fora
          e.preventDefault();
        }}
      >
        <DialogHeader className="p-6 pb-2">
          <DialogTitle>
            {plano_saude ? "Editar Plano de Saúde" : "Novo Plano de Saúde"}
          </DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-y-auto p-6 pt-2">
          <PlanoSaudeForm
            plano_saude={plano_saude}
            onSubmit={handleSubmit}
            onCancel={onClose}
            onSuccess={onSuccess}
            id="plano-saude-form"
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
              type="submit"
              form="plano-saude-form"
              disabled={isSubmitting}
            >
              {isSubmitting 
                ? "Processando..." 
                : plano_saude ? "Atualizar" : "Cadastrar"
              }
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
