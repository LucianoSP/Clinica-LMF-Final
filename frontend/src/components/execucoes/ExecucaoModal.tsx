import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ExecucaoForm } from "./ExecucaoForm";
import { Execucao, ExecucaoFormData } from "@/types/execucao";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { execucaoService } from "@/services/execucaoService";

interface ExecucaoModalProps {
    isOpen: boolean;
    onClose: () => void;
    execucao?: Execucao;
    onSuccess?: () => void;
}

export function ExecucaoModal({ isOpen, onClose, execucao, onSuccess }: ExecucaoModalProps) {
    const queryClient = useQueryClient();

    const handleSubmit = async (formData: ExecucaoFormData) => {
        try {
            if (execucao) {
                // Atualização de registro existente
                await execucaoService.atualizar(execucao.id, formData);
                toast.success('Execução atualizada com sucesso');
            } else {
                // Criação de novo registro
                await execucaoService.criar(formData);
                toast.success('Execução criada com sucesso');
            }

            await queryClient.invalidateQueries({ queryKey: ['execucoes'] });
            onSuccess?.();
            onClose();
        } catch (error: any) {
            console.error('Erro ao salvar execução:', error);
          
            if (error.message?.includes('AuthSessionMissingError')) {
                toast.error('Sessão expirada. Por favor, faça login novamente.');
                return;
            }
          
            const acao = execucao ? 'atualizar' : 'criar';
            toast.error(`Erro ao ${acao} execução. Por favor, tente novamente.`);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>
                        {execucao ? "Editar Execução" : "Nova Execução"}
                    </DialogTitle>
                </DialogHeader>
                <ExecucaoForm
                    execucao={execucao}
                    onSubmit={handleSubmit}
                />
            </DialogContent>
        </Dialog>
    );
}