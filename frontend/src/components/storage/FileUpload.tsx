import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getCurrentUserId } from '@/services/api';
import { storageService } from "@/services/storageService";
import { Storage } from "@/types/storage";

interface FileUploadProps {
    entidade: string;
    entidade_id: string;
    onSuccess?: (file: Storage) => void;
    onError?: (error: any) => void;
}

export function FileUpload({ entidade, entidade_id, onSuccess, onError }: FileUploadProps) {
    const queryClient = useQueryClient();

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            const result = await storageService.upload(file, entidade, entidade_id);
            await queryClient.invalidateQueries({ queryKey: ['storage', entidade, entidade_id] });
            toast.success('Arquivo enviado com sucesso');
            if (result.data) {
                onSuccess?.(result.data);
            }
        } catch (error) {
            console.error('Erro ao enviar arquivo:', error);
            toast.error('Erro ao enviar arquivo');
            onError?.(error);
        }
    };

    return (
        <input
            type="file"
            onChange={handleFileChange}
            className="file-input file-input-bordered w-full max-w-xs"
        />
    );
} 