import { useState } from "react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sessao, SessaoFormData } from "@/types/sessao";
import { sessaoService } from "@/services/sessaoService";
import { SessaoForm } from "./SessaoForm";
import { useQueryClient } from "@tanstack/react-query";
import { getCurrentUserId } from '@/services/api';

interface SessaoModalProps {
    isOpen: boolean;
    onClose: () => void;
    sessao?: Sessao;
}

export function SessaoModal({ isOpen, onClose, sessao }: SessaoModalProps) {
    const [loading, setLoading] = useState(false);
    const queryClient = useQueryClient();

    const handleSubmit = async (data: SessaoFormData) => {
        try {
            const userId = await getCurrentUserId();
            const payload = {
                ...data,
                created_by: userId,
                updated_by: userId
            };
            await sessaoService.criar(payload);
            await queryClient.invalidateQueries({ queryKey: ['sessoes'] });
            toast.success('Sessão criada com sucesso');
            onClose();
        } catch (error) {
            console.error('Erro ao salvar sessão:', error);
            toast.error('Erro ao salvar sessão');
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-[800px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>{sessao ? 'Editar' : 'Nova'} Sessão</DialogTitle>
                </DialogHeader>
                
                <SessaoForm 
                    onSubmit={handleSubmit} 
                    sessao={sessao}
                    loading={loading} 
                />
            </DialogContent>
        </Dialog>
    );
} 