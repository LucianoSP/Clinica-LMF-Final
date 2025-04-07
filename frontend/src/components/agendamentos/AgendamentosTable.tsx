import { Agendamento } from "@/types/agendamento";
import { columns, Column } from "./columns";
import { TableActions } from "@/components/ui/table-actions";
import { ReactNode, useState, useEffect } from "react";

interface AgendamentosTableProps {
    data: Agendamento[];
    isLoading: boolean;
    pageCount: number;
    pageIndex: number;
    onPageChange: (page: number) => void;
    onSort: (column: string, direction: "asc" | "desc") => void;
    sortColumn: string;
    sortDirection: "asc" | "desc";
    onEdit: (agendamento: Agendamento) => void;
    onDelete: (id: string) => void;
}

export function AgendamentosTable({
    data,
    isLoading,
    pageCount,
    pageIndex,
    onPageChange,
    onSort,
    sortColumn,
    sortDirection,
    onEdit,
    onDelete
}: AgendamentosTableProps) {
    // Estado para controlar quais colunas estão visíveis
    const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>({});
    const [showColumnSelector, setShowColumnSelector] = useState(false);

    // Inicializar as colunas visíveis com base na propriedade visibleByDefault
    useEffect(() => {
        const initialVisibility: Record<string, boolean> = {};
        columns.forEach(column => {
            initialVisibility[column.key] = column.visibleByDefault !== false;
        });
        // Sempre manter a coluna de ações visível
        initialVisibility['actions'] = true;
        setVisibleColumns(initialVisibility);
    }, []);

    // Alternância de visibilidade de coluna
    const toggleColumnVisibility = (key: string) => {
        setVisibleColumns(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    // Definindo a coluna de ações
    const actionColumn: Column<Agendamento> = {
        key: "actions",
        label: "Ações",
        render: (_, agendamento: Agendamento) => (
            <TableActions
                onEdit={() => onEdit(agendamento)}
                onDelete={() => onDelete(agendamento.id)}
            />
        ),
        visibleByDefault: true,
    };

    // Filtrar apenas colunas visíveis
    const visibleColumnsArray = [...columns, actionColumn].filter(
        column => visibleColumns[column.key]
    );

    // Renderização manual da tabela
    return (
        <div className="w-full">
            <div className="flex justify-between items-center mb-2">
                <button 
                    className="px-3 py-1 text-xs rounded border bg-gray-50 hover:bg-gray-100"
                    onClick={() => setShowColumnSelector(!showColumnSelector)}
                >
                    {showColumnSelector ? "Esconder" : "Mostrar"} seletor de colunas
                </button>
            </div>

            {showColumnSelector && (
                <div className="mb-4 p-2 border-b bg-gray-50">
                    <div className="text-xs font-medium mb-2">Selecione as colunas:</div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
                        {[...columns, actionColumn].map(column => (
                            <label key={column.key} className="flex items-center space-x-1">
                                <input 
                                    type="checkbox" 
                                    checked={!!visibleColumns[column.key]} 
                                    onChange={() => toggleColumnVisibility(column.key)}
                                    disabled={column.key === 'actions'} // Não permitir desabilitar as ações
                                    className="w-3 h-3"
                                />
                                <span className="text-xs truncate max-w-[90px]" title={column.label}>{column.label}</span>
                            </label>
                        ))}
                    </div>
                </div>
            )}

            {isLoading ? (
                <div className="flex justify-center items-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            ) : (
                <>
                    <div className="w-full overflow-x-auto">
                        <table className="w-full border-collapse text-xs">
                            <thead>
                                <tr className="bg-muted">
                                    {visibleColumnsArray.map((column) => (
                                        <th 
                                            key={column.key}
                                            className="p-2 text-left text-xs font-medium text-muted-foreground cursor-pointer hover:bg-muted/80 whitespace-nowrap"
                                            onClick={() => onSort(column.key, sortColumn === column.key 
                                                ? (sortDirection === "asc" ? "desc" : "asc") 
                                                : "asc")}
                                        >
                                            <div className="flex items-center">
                                                {column.label}
                                                {sortColumn === column.key && (
                                                    <span className="ml-1">
                                                        {sortDirection === "asc" ? "↑" : "↓"}
                                                    </span>
                                                )}
                                            </div>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {data.length === 0 ? (
                                    <tr>
                                        <td colSpan={visibleColumnsArray.length} className="p-4 text-center text-muted-foreground">
                                            Nenhum agendamento encontrado
                                        </td>
                                    </tr>
                                ) : (
                                    data.map((agendamento, index) => (
                                        <tr 
                                            key={agendamento.id} 
                                            className={`border-b hover:bg-muted/50 ${index % 2 === 0 ? 'bg-white' : 'bg-muted/20'}`}
                                        >
                                            {visibleColumnsArray.map((column) => (
                                                <td key={`${agendamento.id}-${column.key}`} className="p-2 text-xs whitespace-nowrap overflow-hidden text-ellipsis" style={{maxWidth: '150px'}}>
                                                    {column.render(null, agendamento)}
                                                </td>
                                            ))}
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Paginação simples */}
                    {pageCount > 1 && (
                        <div className="flex items-center justify-between p-2 border-t">
                            <div className="text-xs text-muted-foreground">
                                Página {pageIndex + 1} de {pageCount}
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => onPageChange(Math.max(0, pageIndex - 1))}
                                    disabled={pageIndex === 0}
                                    className="px-3 py-1 text-xs rounded border disabled:opacity-50 bg-white hover:bg-gray-50"
                                >
                                    Anterior
                                </button>
                                <button
                                    onClick={() => onPageChange(Math.min(pageCount - 1, pageIndex + 1))}
                                    disabled={pageIndex === pageCount - 1}
                                    className="px-3 py-1 text-xs rounded border disabled:opacity-50 bg-white hover:bg-gray-50"
                                >
                                    Próxima
                                </button>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
} 