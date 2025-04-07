import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { FichaForm } from "./FichaForm";
import { Ficha, FichaData } from "@/types/ficha";
import { fichaService } from "@/services/fichaService";
import { getCurrentUserId } from '@/services/api';
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface FichaModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: Ficha;
}

export function FichaModal({ isOpen, onClose, initialData }: FichaModalProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (formData: FichaData) => {
    try {
      setIsSubmitting(true);
      const userId = await getCurrentUserId();
      const data = {
        ...formData,
        updated_by: userId,
        created_by: initialData?.id ? undefined : userId
      };
      
      if (initialData?.id) {
        await fichaService.atualizar(initialData.id, data);
        toast.success("Ficha atualizada com sucesso!");
      } else {
        await fichaService.criar(data);
        toast.success("Ficha criada com sucesso!");
      }
      
      queryClient.invalidateQueries({ queryKey: ['fichas'] });
      onClose();
    } catch (error) {
      console.error('Erro ao salvar ficha:', error);
      toast.error('Erro ao salvar ficha');
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
        onOpenAutoFocus={(e) => e.preventDefault()}
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
            {initialData ? "Editar Ficha" : "Nova Ficha"}
          </DialogTitle>
          {!initialData && (
            <DialogDescription>
              Preencha os dados da ficha
            </DialogDescription>
          )}
        </DialogHeader>
        <div className="flex-1 overflow-y-auto p-6 pt-2">
          <FichaForm
            ficha={initialData}
            onSubmit={handleSubmit}
            onCancel={onClose}
            loading={isSubmitting}
            id="ficha-form"
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
              form="ficha-form"
              disabled={isSubmitting}
            >
              {isSubmitting 
                ? "Processando..." 
                : initialData ? "Atualizar" : "Cadastrar"
              }
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}