import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ArrowUpDown, ChevronDown, ChevronUp } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export interface Column<T> {
  key: string;
  label: string;
  render?: (value: unknown, item: T) => React.ReactNode;
  sortable?: boolean;
}

interface SortableTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pageCount: number;
  pageIndex: number;
  pageSize: number;
  totalRecords: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newSize: number) => void;
  sortable?: boolean;
  onSort?: (column: string, direction: "asc" | "desc") => void;
  lastUpdateDate?: string;
}

export function SortableTable<T>({
  data,
  columns,
  loading = false,
  pageCount,
  pageIndex,
  pageSize,
  totalRecords,
  onPageChange,
  onPageSizeChange,
  sortable = false,
  onSort,
  lastUpdateDate,
}: SortableTableProps<T>) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const handleSort = (column: string) => {
    if (!sortable || !onSort) return;

    const newDirection = 
      sortColumn === column && sortDirection === "asc" ? "desc" : "asc";
    
    setSortColumn(column);
    setSortDirection(newDirection);
    onSort(column, newDirection);
  };

  const formatDateTime = (date: string | undefined) => {
    if (!date) return "";
    return new Date(date).toLocaleString("pt-BR");
  };

  return (
    <div className="rounded-md border bg-white">
      <div className="px-4 py-2">
        <Table>
          <TableHeader className="bg-slate-50">
            <TableRow className="hover:bg-transparent border-b border-slate-200">
              {columns.map((column) => (
                <TableHead 
                  key={column.key}
                  className="py-3 px-4 text-slate-700 font-medium"
                  onClick={() => handleSort(column.key as string)}
                >
                  <div className="flex items-center gap-1">
                    {column.label}
                    {sortable && (
                      <div className="flex flex-col">
                        {sortColumn === column.key ? (
                          sortDirection === "asc" ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )
                        ) : (
                          <ArrowUpDown className="h-4 w-4" />
                        )}
                      </div>
                    )}
                  </div>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-slate-500"
                >
                  Carregando...
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-slate-500"
                >
                  Nenhum registro encontrado.
                </TableCell>
              </TableRow>
            ) : (
              data.map((item, index) => (
                <TableRow 
                  key={index}
                  className="border-b border-slate-100 hover:bg-slate-50/50"
                >
                  {columns.map((column) => (
                    <TableCell 
                      key={column.key}
                      className="py-3 px-4"
                    >
                      {column.render
                        ? column.render(item[column.key as keyof T], item)
                        : item[column.key as keyof T]?.toString() || "-"}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between py-3 px-4 border-t border-slate-200 bg-slate-50">
        <div className="flex items-center gap-4">
          <p className="text-sm text-slate-600">
            Página {pageIndex + 1} de {pageCount}
          </p>
          <div className="flex items-center gap-2">
            {onPageSizeChange && (
              <>
                <Select
                  value={pageSize.toString()}
                  onValueChange={(value: string) => onPageSizeChange(Number(value))}
                >
                  <SelectTrigger className="h-8 w-[70px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[10, 20, 30, 40, 50].map((size) => (
                      <SelectItem key={size} value={size.toString()}>
                        {size}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-sm text-slate-600">
                  registros por página
                </span>
              </>
            )}
            <span className="text-sm text-slate-600 ml-2">
              • Total: {totalRecords} registros
              {lastUpdateDate && (
                <span className="ml-2">• Última atualização: {formatDateTime(lastUpdateDate)}</span>
              )}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(0)}
            disabled={pageIndex === 0}
          >
            {"<<"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pageIndex - 1)}
            disabled={pageIndex === 0}
          >
            {"<"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pageIndex + 1)}
            disabled={pageIndex === pageCount - 1}
          >
            {">"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pageCount - 1)}
            disabled={pageIndex === pageCount - 1}
          >
            {">>"}
          </Button>
        </div>
      </div>
    </div>
  );
}