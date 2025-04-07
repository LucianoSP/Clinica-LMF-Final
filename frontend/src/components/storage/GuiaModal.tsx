import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { GuiaForm } from "./GuiaForm";
import { Guia, GuiaFormData } from "@/types/guia";
import { guiaService } from "@/services/guiaService";

interface GuiaModalProps {
  isOpen: boolean;
  onClose: () => void;
  guia?: Guia;
}

export function GuiaModal({ isOpen, onClose, guia }: GuiaModalProps) {
  const queryClient = useQueryClient();

  const handleSubmit = async (data: GuiaFormData) => {
    try {
      if (guia?.id) {
        await guiaService.atualizar(guia.id, data);
        toast.success("Guia atualizada com sucesso!");
      } else {
        await guiaService.criar(data);
        toast.success("Guia cadastrada com sucesso!");
      }
      
      queryClient.invalidateQueries({ queryKey: ["guias"] });
      onClose();
    } catch (error) {
      console.error("Erro ao salvar guia:", error);
      toast.error("Erro ao salvar guia");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent 
        className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto"
        onOpenAutoFocus={(e) => e.preventDefault()}
      >
        <DialogHeader>
          <DialogTitle>
            {guia ? "Editar Guia" : "Nova Guia"}
          </DialogTitle>
        </DialogHeader>
        <GuiaForm
          guia={guia}
          onSubmit={handleSubmit}
          onCancel={onClose}
        />
      </DialogContent>
    </Dialog>
  );
} 