"use client";

import { useState } from "react";
import { Ficha, FichaData } from "@/types/ficha";
import { useFichas } from "@/hooks/useFichas";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus, ChevronLeft, FileDown, Upload, ListFilter } from "lucide-react";
import { FichaModal } from "@/components/fichas/FichaModal";
import { FileUpload } from "@/components/fichas/FileUpload";
import { SortableTable } from "@/components/ui/SortableTable";
import { createColumns } from "@/components/fichas/columns";
import { useDebounce } from "@/hooks/useDebounce";
import { fichaService } from "@/services/fichaService";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FichasPendentesTab } from "@/components/fichas/FichasPendentesTab";
import { ProcessarFichaModal } from "@/components/fichas/ProcessarFichaModal";
import Link from "next/link";
import * as XLSX from 'xlsx';
import React from "react";

// Memoize o componente FichasPendentesTab para evitar renderizações desnecessárias
const MemoizedFichasPendentesTab = React.memo(FichasPendentesTab);

export default function FichasPage() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedFicha, setSelectedFicha] = useState<Ficha | undefined>();
    const [fichaToProcess, setFichaToProcess] = useState<Ficha | null>(null);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [fichaToDelete, setFichaToDelete] = useState<string | null>(null);
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
    const [isProcessModalOpen, setIsProcessModalOpen] = useState(false);
    const [activeTab, setActiveTab] = useState("fichas");
    const [orderColumn, setOrderColumn] = useState<string>("data_atendimento");
    const [orderDirection, setOrderDirection] = useState<"asc" | "desc">("desc");

    const debouncedSearch = useDebounce(search, 500);

    const { data, isLoading, refetch } = useFichas(
        page,
        limit,
        debouncedSearch,
        orderColumn,
        orderDirection
    );

    const handleDelete = async (id: string) => {
        try {
            await fichaService.excluir(id);
            toast.success("Ficha excluída com sucesso!");
            refetch();
        } catch (error) {
            console.error("Erro ao excluir ficha:", error);
            toast.error("Erro ao excluir ficha");
        }
    };

    const columns = createColumns({
        onEdit: (ficha) => {
            setSelectedFicha(ficha);
            setIsModalOpen(true);
        },
        onDelete: handleDelete,
        onViewSessoes: (ficha) => {
            setFichaToProcess(ficha);
            setIsProcessModalOpen(true);
        }
    });

    const handleExportToExcel = () => {
        try {
            const exportData = data?.items.map(ficha => ({
                'Código': ficha.codigo_ficha || '-',
                'Número da Guia': ficha.numero_guia,
                'Nome do Paciente': ficha.paciente_nome,
                'Carteirinha': ficha.paciente_carteirinha,
                'Data do Atendimento': formatarData(ficha.data_atendimento),
                'Status': ficha.status.charAt(0).toUpperCase() + ficha.status.slice(1),
                'Sessões Conferidas': ficha.sessoes_conferidas || '0',
                'Data de Criação': formatarData(ficha.created_at)
            }));

            if (!exportData) return;

            const ws = XLSX.utils.json_to_sheet(exportData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Fichas');
            XLSX.writeFile(wb, 'fichas.xlsx');

            toast.success('Dados exportados com sucesso!');
        } catch (error) {
            console.error('Erro ao exportar dados:', error);
            toast.error('Erro ao exportar dados');
        }
    };

    // Função para lidar com o processamento da ficha após edição das sessões
    const handleProcessarFicha = (ficha: Ficha) => {
        refetch();
        toast.success(`Sessões da ficha ${ficha.codigo_ficha} atualizadas com sucesso!`);
    };

    // Função auxiliar para formatar datas
    const formatarData = (dataString: string | null | undefined): string => {
        if (!dataString) return '-';
        try {
            const data = new Date(dataString);
            return data.toLocaleDateString('pt-BR');
        } catch (e) {
            return dataString || '-';
        }
    };

    return (
        <div className="p-8">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    <h1 className="text-2xl font-semibold text-slate-900">Fichas de Presença</h1>
                    <Link
                        href="/cadastros"
                        className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
                    >
                        <ChevronLeft className="h-4 w-4" />
                        Voltar
                    </Link>
                </div>
                <p className="text-slate-500">Gerencie as fichas de presença</p>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="mb-4">
                    <TabsTrigger value="fichas">Fichas</TabsTrigger>
                    <TabsTrigger value="pendentes">Fichas Pendentes</TabsTrigger>
                </TabsList>
                
                <TabsContent value="fichas">
                    <div className="flex justify-between items-center gap-4 mb-4">
                        <Input
                            placeholder="Buscar fichas..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="max-w-sm"
                        />
                        <div className="flex gap-2">
                            <Button
                                onClick={() => setIsUploadModalOpen(true)}
                                variant="outline"
                                className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                            >
                                <Upload className="mr-2 h-4 w-4" />
                                Upload PDF
                            </Button>
                            <Button
                                onClick={handleExportToExcel}
                                variant="outline"
                                className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                            >
                                <FileDown className="mr-2 h-4 w-4" />
                                Exportar Excel
                            </Button>
                            <Button
                                onClick={() => {
                                    setSelectedFicha(undefined);
                                    setIsModalOpen(true);
                                }}
                                variant="outline"
                                className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
                            >
                                <Plus className="mr-2 h-4 w-4" />
                                Nova Ficha
                            </Button>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg border shadow-sm">
                        <SortableTable
                            data={data?.items || []}
                            columns={columns}
                            loading={isLoading}
                            pageCount={data?.total_pages || 0}
                            pageIndex={page - 1}
                            pageSize={limit}
                            totalRecords={data?.total || 0}
                            onPageChange={(newPage) => setPage(newPage + 1)}
                            onPageSizeChange={setLimit}
                            sortable
                            onSort={(column, direction) => {
                                setOrderColumn(column);
                                setOrderDirection(direction);
                            }}
                        />
                    </div>
                </TabsContent>
                
                <TabsContent value="pendentes">
                    <MemoizedFichasPendentesTab />
                </TabsContent>
            </Tabs>

            {/* Modal de criação/edição de ficha */}
            <FichaModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                initialData={selectedFicha}
            />

            {/* Modal de upload de PDF */}
            <Dialog open={isUploadModalOpen} onOpenChange={setIsUploadModalOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Upload de Ficha PDF</DialogTitle>
                        <DialogDescription>
                            Faça upload do arquivo PDF da ficha para processamento automático.
                        </DialogDescription>
                    </DialogHeader>
                    <FileUpload
                        isOpen={isUploadModalOpen}
                        onClose={() => {
                            setIsUploadModalOpen(false);
                            refetch();
                            setActiveTab("pendentes");
                        }}
                    />
                </DialogContent>
            </Dialog>

            {/* Modal de processamento de ficha (edição de sessões) */}
            <ProcessarFichaModal
                ficha={fichaToProcess}
                isOpen={isProcessModalOpen}
                onClose={() => setIsProcessModalOpen(false)}
                onProcessar={handleProcessarFicha}
            />
        </div>
    );
}