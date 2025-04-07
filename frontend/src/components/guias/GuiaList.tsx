import { useState } from "react"
import { useGuias } from "@/hooks/useGuias"
import { Guia, GuiaFilters, GuiaStatus, TipoGuia } from "@/types/guia"
import { formatarData } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { LoadingSpinner } from "../ui/loading"
import { GuiaModal } from "./GuiaModal"
import { Pagination } from "../ui/pagination"

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

interface GuiaListProps {
    initialFilters?: GuiaFilters
}

export function GuiaList({ initialFilters }: GuiaListProps) {
    const [page, setPage] = useState(1)
    const [limit] = useState(10)
    const [filters, setFilters] = useState<GuiaFilters>(initialFilters || {})
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [selectedGuia, setSelectedGuia] = useState<Guia>()

    const { data, isLoading, isError } = useGuias(page, limit, filters)

    const handleSearch = (search: string) => {
        setFilters(prev => ({ ...prev, search }))
        setPage(1)
    }

    const handleStatusFilter = (status: GuiaStatus) => {
        setFilters(prev => ({ ...prev, status }))
        setPage(1)
    }

    const handleTipoFilter = (tipo: TipoGuia) => {
        setFilters(prev => ({ ...prev, tipo }))
        setPage(1)
    }

    const handleEdit = (guia: Guia) => {
        setSelectedGuia(guia)
        setIsModalOpen(true)
    }

    const handleCloseModal = () => {
        setSelectedGuia(undefined)
        setIsModalOpen(false)
    }

    if (isError) {
        return (
            <div className="text-center text-red-500">
                Erro ao carregar as guias. Por favor, tente novamente.
            </div>
        )
    }

    const getStatusBadge = (status: GuiaStatus) => {
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
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Input
                        placeholder="Buscar guias..."
                        className="w-[300px]"
                        value={filters.search || ''}
                        onChange={(e) => handleSearch(e.target.value)}
                    />
                    <Select
                        value={filters.status}
                        onValueChange={(value) => handleStatusFilter(value as GuiaStatus)}
                    >
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            {statusOptions.map(option => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Select
                        value={filters.tipo}
                        onValueChange={(value) => handleTipoFilter(value as TipoGuia)}
                    >
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Tipo" />
                        </SelectTrigger>
                        <SelectContent>
                            {tipoOptions.map(option => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
                <Button onClick={() => setIsModalOpen(true)}>
                    Nova Guia
                </Button>
            </div>

            {isLoading ? (
                <div className="flex justify-center p-8">
                    <div className="text-slate-500">Carregando...</div>
                </div>
            ) : (
                <>
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Número</TableHead>
                                    <TableHead>Data Solicitação</TableHead>
                                    <TableHead>Tipo</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Quantidade</TableHead>
                                    <TableHead>Ações</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data?.items.map((guia) => (
                                    <TableRow key={guia.id}>
                                        <TableCell>{guia.numero_guia}</TableCell>
                                        <TableCell>{formatarData(guia.data_solicitacao)}</TableCell>
                                        <TableCell>
                                            {tipoOptions.find(t => t.value === guia.tipo)?.label}
                                        </TableCell>
                                        <TableCell>
                                            {getStatusBadge(guia.status)}
                                        </TableCell>
                                        <TableCell>
                                            {guia.quantidade_solicitada}
                                            {guia.quantidade_autorizada && (
                                                <span className="text-sm text-gray-500">
                                                    {" "}
                                                    (Autorizado: {guia.quantidade_autorizada})
                                                </span>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            <Button
                                                variant="ghost"
                                                onClick={() => handleEdit(guia)}
                                            >
                                                Editar
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>

                    <Pagination
                        pageCount={data?.total_pages || 0}
                        pageIndex={page - 1} // converte para 0-based
                        pageSize={10}
                        totalRecords={data?.total || 0}
                        onPageChange={(newPage) => setPage(newPage + 1)} // converte para 1-based
                    />
                </>
            )}

            <GuiaModal
                open={isModalOpen}
                onOpenChange={handleCloseModal}
                initialData={selectedGuia}
            />
        </div>
    )
}