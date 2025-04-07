import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getCurrentUserId } from '@/services/api';
import { divergenciaService } from "@/services/divergenciaService";
import { Divergencia, DivergenciaFormData } from "@/types/divergencia";

interface DivergenciaModalProps {
    isOpen: boolean;
    onClose: () => void;
    divergencia?: Divergencia;
}

export function DivergenciaModal({ isOpen, onClose, divergencia }: DivergenciaModalProps) {
    const queryClient = useQueryClient();

    const handleSubmit = async (data: DivergenciaFormData) => {
        try {
            const userId = await getCurrentUserId();
            const payload = {
                ...data,
                created_by: userId,
                updated_by: userId
            };
            await divergenciaService.criar(payload);
            await queryClient.invalidateQueries({ queryKey: ['divergencias'] });
            toast.success('Divergência criada com sucesso');
            onClose();
        } catch (error) {
            console.error('Erro ao salvar divergência:', error);
            toast.error('Erro ao salvar divergência');
        }
    };

    // ... resto do código
} 