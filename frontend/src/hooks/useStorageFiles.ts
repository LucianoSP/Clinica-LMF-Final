import { useQuery } from "@tanstack/react-query"
import { storageService, StorageListParams } from "@/services/storageService"
import { StandardResponse } from "@/types/api"
import { Storage } from "@/types/storage"

export function useStorageFiles(params: StorageListParams = {}) {
    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["storage", params],
        queryFn: () => storageService.listar(params),
        staleTime: 1000 * 60 // 1 minute
    })

    return {
        data,
        isLoading,
        error,
        refetch
    }
}

export function useStorageFilesByReference(referenceId?: string, referenceType?: string) {
    const { data, isLoading, error, refetch } = useQuery<StandardResponse<Storage[]>>({
        queryKey: ["storage", referenceId, referenceType],
        queryFn: () => {
            if (!referenceId || !referenceType) return Promise.resolve({ data: [], success: true } as StandardResponse<Storage[]>)
            return storageService.buscarPorReferencia(referenceId, referenceType)
        },
        enabled: !!referenceId && !!referenceType,
        staleTime: 1000 * 60 // 1 minute
    })

    return {
        files: data?.data || [],
        isLoading,
        error,
        refetch
    }
}