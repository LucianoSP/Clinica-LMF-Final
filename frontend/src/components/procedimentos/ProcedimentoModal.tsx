import { useState } from "react";
import { toast } from "sonner";
import { Procedimento, ProcedimentoCreate } from "@/types/procedimento";
import { procedimentoService } from "@/services/procedimentoService";
import { 
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ProcedimentoForm } from "./ProcedimentoForm";
import { useQueryClient } from "@tanstack/react-query";
import { getCurrentUserId } from '@/services/api';
import { Loader2 } from "lucide-react";

interface ProcedimentoModalProps {
    isOpen: boolean;
    onClose: () => void;
    procedimento?: Procedimento;
}

export function ProcedimentoModal({
    isOpen,
    onClose,
    procedimento,
}: ProcedimentoModalProps) {
    const [loading, setLoading] = useState(false);
    const queryClient = useQueryClient();

    const handleSubmit = async (data: ProcedimentoCreate) => {
        try {
            setLoading(true);
            const userId = await getCurrentUserId();
            const payload = {
                ...data,
                created_by: userId,
                updated_by: userId
            };
            if (procedimento) {
                await procedimentoService.atualizar(procedimento.id, payload);
                toast.success("Procedimento atualizado com sucesso!");
            } else {
                await procedimentoService.criar(payload);
                toast.success("Procedimento criado com sucesso!");
            }
            await queryClient.invalidateQueries({ queryKey: ["procedimentos"] });
            onClose();
        } catch (error) {
            console.error("Erro ao salvar procedimento:", error);
            toast.error("Erro ao salvar procedimento");
        } finally {
            setLoading(false);
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
                        {procedimento ? "Editar Procedimento" : "Novo Procedimento"}
                    </DialogTitle>
                    {!procedimento && (
                        <DialogDescription>
                            Preencha os dados do procedimento
                        </DialogDescription>
                    )}
                </DialogHeader>

                <div className="flex-1 overflow-y-auto p-6 pt-2">
                    <ProcedimentoForm
                        onSubmit={handleSubmit}
                        procedimento={procedimento}
                        loading={loading}
                        id="procedimento-form"
                    />
                </div>

                <div className="border-t p-4 bg-background">
                    <div className="flex justify-end space-x-2">
                        <Button 
                            type="button" 
                            variant="outline" 
                            onClick={onClose}
                            disabled={loading}
                        >
                            Cancelar
                        </Button>
                        <Button 
                            type="submit"
                            form="procedimento-form"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    {procedimento ? 'Salvando...' : 'Criando...'}
                                </>
                            ) : (
                                procedimento ? 'Salvar' : 'Criar'
                            )}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}