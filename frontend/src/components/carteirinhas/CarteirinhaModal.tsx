import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CarteirinhaForm } from "./CarteirinhaForm";
import { Carteirinha, CarteirinhaFormData } from "@/types/carteirinha";
import { carteirinhaService } from "@/services/carteirinhaService";
import { getCurrentUserId } from "@/services/api";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface CarteirinhaModalProps {
  isOpen: boolean;
  onClose: () => void;
  carteirinha?: Carteirinha;
}

export function CarteirinhaModal({ isOpen, onClose, carteirinha }: CarteirinhaModalProps) {
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (formData: CarteirinhaFormData) => {
    try {
      setIsSubmitting(true);
      const userId = await getCurrentUserId();

      const data = {
        ...formData,
        updated_by: userId,
        created_by: carteirinha?.id ? undefined : userId
      };

      if (carteirinha?.id) {
        await carteirinhaService.atualizar(carteirinha.id, data);
        toast.success("Carteirinha atualizada com sucesso!");
      } else {
        await carteirinhaService.criar(data);
        toast.success("Carteirinha cadastrada com sucesso!");
      }

      queryClient.invalidateQueries({ queryKey: ["carteirinhas"] });
      onClose();
    } catch (error) {
      console.error("Erro ao salvar carteirinha:", error);
      toast.error("Erro ao salvar carteirinha");
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
            {carteirinha ? "Editar Carteirinha" : "Nova Carteirinha"}
          </DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-y-auto p-6 pt-2">
          <CarteirinhaForm
            carteirinha={carteirinha}
            onSubmit={handleSubmit}
            onCancel={onClose}
            id="carteirinha-form"
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
              form="carteirinha-form"
              disabled={isSubmitting}
            >
              {isSubmitting 
                ? "Processando..." 
                : carteirinha ? "Atualizar" : "Cadastrar"
              }
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
