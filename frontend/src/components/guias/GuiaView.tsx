import { Guia } from "@/types/guia"
import { formatarData } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { GuiaModal } from "./GuiaModal"
import { useState } from "react"

const tipoOptions = [
    { value: 'consulta', label: 'Consulta' },
    { value: 'exame', label: 'Exame' },
    { value: 'procedimento', label: 'Procedimento' },
    { value: 'internacao', label: 'Internação' },
] as const

const statusOptions = [
    { value: 'rascunho', label: 'Rascunho' },
    { value: 'pendente', label: 'Pendente' },
    { value: 'autorizada', label: 'Autorizada' },
    { value: 'negada', label: 'Negada' },
    { value: 'cancelada', label: 'Cancelada' },
    { value: 'executada', label: 'Executada' },
] as const

interface GuiaViewProps {
    guia: Guia
    onEdit?: () => void
}

export function GuiaView({ guia, onEdit }: GuiaViewProps) {
    const [isModalOpen, setIsModalOpen] = useState(false)

    const getStatusBadge = (status: Guia['status']) => {
        const variants = {
            rascunho: 'outline',
            pendente: 'warning',
            autorizada: 'success',
            negada: 'destructive',
            cancelada: 'outline',
            executada: 'default'
        } as const;

        return (
            <Badge variant={variants[status]}>
                {statusOptions.find(s => s.value === status)?.label}
            </Badge>
        )
    }

    return (
        <>
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-2xl font-bold">
                        Guia {guia.numero_guia}
                    </CardTitle>
                    <Button onClick={() => setIsModalOpen(true)}>
                        Editar Guia
                    </Button>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <h3 className="font-semibold">Informações Gerais</h3>
                            <div className="space-y-2 mt-2">
                                <div>
                                    <span className="text-sm text-gray-500">Status:</span>
                                    <div className="mt-1">{getStatusBadge(guia.status)}</div>
                                </div>
                                <div>
                                    <span className="text-sm text-gray-500">Tipo:</span>
                                    <div className="mt-1">
                                        {tipoOptions.find(t => t.value === guia.tipo)?.label}
                                    </div>
                                </div>
                                <div>
                                    <span className="text-sm text-gray-500">Data de Solicitação:</span>
                                    <div className="mt-1">{formatarData(guia.data_solicitacao)}</div>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 className="font-semibold">Quantidades</h3>
                            <div className="space-y-2 mt-2">
                                <div>
                                    <span className="text-sm text-gray-500">Solicitada:</span>
                                    <div className="mt-1">{guia.quantidade_solicitada}</div>
                                </div>
                                {guia.quantidade_autorizada && (
                                    <div>
                                        <span className="text-sm text-gray-500">Autorizada:</span>
                                        <div className="mt-1">{guia.quantidade_autorizada}</div>
                                    </div>
                                )}
                                {guia.quantidade_executada > 0 && (
                                    <div>
                                        <span className="text-sm text-gray-500">Executada:</span>
                                        <div className="mt-1">{guia.quantidade_executada}</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {guia.dados_autorizacao && (
                        <div>
                            <h3 className="font-semibold mb-2">Dados da Autorização</h3>
                            <div className="grid grid-cols-2 gap-4">
                                {guia.dados_autorizacao.autorizador && (
                                    <div>
                                        <span className="text-sm text-gray-500">Autorizador:</span>
                                        <div className="mt-1">{guia.dados_autorizacao.autorizador}</div>
                                    </div>
                                )}
                                {guia.dados_autorizacao.codigo_autorizacao && (
                                    <div>
                                        <span className="text-sm text-gray-500">Código:</span>
                                        <div className="mt-1">{guia.dados_autorizacao.codigo_autorizacao}</div>
                                    </div>
                                )}
                                {guia.dados_autorizacao.data_autorizacao && (
                                    <div>
                                        <span className="text-sm text-gray-500">Data:</span>
                                        <div className="mt-1">{formatarData(guia.dados_autorizacao.data_autorizacao)}</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {guia.motivo_negacao && (
                        <div>
                            <h3 className="font-semibold mb-2">Motivo da Negação</h3>
                            <p className="text-gray-700">{guia.motivo_negacao}</p>
                        </div>
                    )}

                    {guia.observacoes && (
                        <div>
                            <h3 className="font-semibold mb-2">Observações</h3>
                            <p className="text-gray-700">{guia.observacoes}</p>
                        </div>
                    )}

                    {guia.historico_status && guia.historico_status.length > 0 && (
                        <div>
                            <h3 className="font-semibold mb-2">Histórico de Status</h3>
                            <div className="space-y-2">
                                {guia.historico_status.map((historico, index) => (
                                    <div key={index} className="flex items-center gap-2">
                                        <Badge variant="outline">
                                            {formatarData(historico.data)}
                                        </Badge>
                                        <Badge>
                                            {statusOptions.find(s => s.value === historico.status)?.label}
                                        </Badge>
                                        <span className="text-sm text-gray-500">
                                            por {historico.usuario}
                                        </span>
                                        {historico.observacao && (
                                            <span className="text-sm text-gray-500">
                                                - {historico.observacao}
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            <GuiaModal
                open={isModalOpen}
                onOpenChange={setIsModalOpen}
                initialData={guia}
                onSuccess={onEdit}
            />
        </>
    )
}