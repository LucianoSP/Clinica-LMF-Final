"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useStorageFiles } from "@/hooks/useStorageFiles"
import { Storage } from "@/types/storage"
import { storageService } from "@/services/storageService"
import { toast } from "sonner"
import { Upload } from "lucide-react"

const formSchema = z.object({
    file: z.instanceof(File).optional(),
    reference_id: z.string().uuid().optional(),
    reference_type: z.string().optional()
})

type StorageModalProps = {
    isOpen: boolean
    onClose: () => void
    storage?: Storage
    referenceId?: string
    referenceType?: string
    onSuccess?: () => void
}

export function StorageModal({ isOpen, onClose, storage, referenceId, referenceType, onSuccess }: StorageModalProps) {
    const [isSubmitting, setIsSubmitting] = useState(false)
    const { refetch } = useStorageFiles()
    const [selectedFile, setSelectedFile] = useState<File | null>(null)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            reference_id: referenceId,
            reference_type: referenceType
        }
    })

    const onSubmit = async (data: z.infer<typeof formSchema>) => {
        try {
            setIsSubmitting(true)
            
            if (!selectedFile) {
                toast.error("Selecione um arquivo para upload")
                return
            }

            const formData = new FormData()
            formData.append("file", selectedFile)
            if (data.reference_id) formData.append("reference_id", data.reference_id)
            if (data.reference_type) formData.append("reference_type", data.reference_type)

            if (storage?.id) {
                await storageService.atualizar(storage.id, formData)
                toast.success("Arquivo atualizado com sucesso!")
            } else {
                await storageService.criar(formData)
                toast.success("Arquivo enviado com sucesso!")
            }

            refetch()
            onSuccess?.()
            handleClose()
        } catch (error) {
            console.error("Erro ao salvar arquivo:", error)
            toast.error("Erro ao salvar arquivo")
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleClose = () => {
        form.reset()
        setSelectedFile(null)
        onClose()
    }

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (file) {
            setSelectedFile(file)
        }
    }

    return (
        <Dialog open={isOpen} onOpenChange={handleClose}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>
                        {storage ? "Editar Arquivo" : "Upload de Arquivo"}
                    </DialogTitle>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="file"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Arquivo</FormLabel>
                                    <FormControl>
                                        <Input 
                                            type="file"
                                            onChange={handleFileChange}
                                            className="cursor-pointer"
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter className="gap-2 pt-4">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleClose}
                                disabled={isSubmitting}
                            >
                                Cancelar
                            </Button>
                            <Button 
                                type="submit"
                                disabled={isSubmitting}
                            >
                                <Upload className="w-4 h-4 mr-2" />
                                {storage ? "Atualizar" : "Enviar"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}