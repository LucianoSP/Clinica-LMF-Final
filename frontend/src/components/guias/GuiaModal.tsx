import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { GuiaForm } from "./GuiaForm";
import { Guia } from "@/types/guia";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Loader2 } from "lucide-react";

interface GuiaModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
  initialData?: Guia;
}

export function GuiaModal({
  open,
  onOpenChange,
  onSuccess,
  initialData
}: GuiaModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSuccess = () => {
    if (onSuccess) {
      onSuccess();
    }
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => {
      // Só permite fechar o modal através dos botões
      if (!isOpen) {
        return;
      }
      onOpenChange(isOpen);
    }}>
      <DialogContent 
        className="max-w-4xl max-h-[90vh] flex flex-col p-0 overflow-hidden"
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
            {initialData ? "Editar Guia" : "Nova Guia"}
          </DialogTitle>
          {!initialData && (
            <DialogDescription>
              Preencha os dados da guia
            </DialogDescription>
          )}
        </DialogHeader>

        <div className="flex-1 overflow-y-auto p-6 pt-2">
          <GuiaForm
            initialData={initialData}
            onSuccess={() => {
              setIsSubmitting(false);
              handleSuccess();
            }}
            onCancel={() => onOpenChange(false)}
            id="guia-form"
            onSubmit={() => setIsSubmitting(true)}
          />
        </div>

        <div className="border-t p-4 bg-background">
          <div className="flex justify-end space-x-2">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button 
              type="submit"
              form="guia-form"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {initialData ? 'Salvando...' : 'Criando...'}
                </>
              ) : (
                initialData ? 'Salvar' : 'Criar'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}