import { Guia, GuiaStatus, TipoGuia } from '@/types/guia';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye, FileDown, Plus } from 'lucide-react';
import { BadgeGuiaStatus } from '@/components/ui/badge-guia-status';
import { SortableTable, Column } from '@/components/ui/SortableTable';
import { formatarData } from '@/lib/utils';
import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { QuantidadeProgress } from '@/components/ui/quantidade-progress';

interface PacienteGuiasProps {
  guias?: Guia[];
  onViewGuia: (guia: Guia) => void;
}

export function PacienteGuias({ 
  guias = [],
  onViewGuia 
}: PacienteGuiasProps) {
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [orderColumn, setOrderColumn] = useState('data_emissao');
  const [orderDirection, setOrderDirection] = useState<'asc' | 'desc'>('desc');

  const columns: Column<Guia>[] = [
    {
      key: 'numero_guia',
      label: 'Número',
      render: (value) => value?.toString() || 'N/A',
    },
    {
      key: 'tipo',
      label: 'Tipo',
      render: (value) => {
        const tipo = value?.toString().toLowerCase() as TipoGuia;
        return <BadgeGuiaStatus value={tipo} />;
      },
    },
    {
      key: 'data_solicitacao',
      label: 'Data Solicitação',
      render: (value) => formatarData(value?.toString()),
    },
    {
      key: 'descricao_servico',
      label: 'Serviço',
      render: (value) => value?.toString() || 'N/A',
    },
    {
      key: 'quantidade',
      label: 'Progresso',
      render: (_, item) => (
        <QuantidadeProgress
          autorizada={item.quantidade_autorizada}
          executada={item.quantidade_executada}
        />
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => {
        const status = value?.toString().toLowerCase() as GuiaStatus;
        return <BadgeGuiaStatus value={status} />;
      },
    },
    {
      key: 'actions',
      label: 'Ações',
      render: (_, item) => (
        <Button variant="ghost" size="sm" onClick={() => onViewGuia(item)}>
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ];

  const filteredData = guias.filter(guia => 
    guia.numero_guia?.toLowerCase().includes(search.toLowerCase()) ||
    guia.descricao_servico?.toLowerCase().includes(search.toLowerCase()) ||
    guia.tipo?.toLowerCase().includes(search.toLowerCase()) ||
    guia.status?.toLowerCase().includes(search.toLowerCase())
  );

  const paginatedData = filteredData.slice((page - 1) * perPage, page * perPage);
  const totalPages = Math.ceil(filteredData.length / perPage);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Guias</CardTitle>
          <div className="flex gap-2">
            <Button 
              variant="outline"
              className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
            >
              <Plus className="mr-2 h-4 w-4" />
              Nova Guia
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center gap-4 mb-4">
          <Input
            placeholder="Buscar guias..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-sm"
          />
        </div>

        <div className="bg-white rounded-lg border shadow-sm">
          <SortableTable
            columns={columns}
            data={paginatedData}
            pageCount={totalPages}
            pageIndex={page - 1}
            pageSize={perPage}
            totalRecords={filteredData.length}
            onPageChange={(newPage: number) => setPage(newPage + 1)}
            onPageSizeChange={(newSize: number) => setPerPage(newSize)}
            sortable
            onSort={(column: string, direction: 'asc' | 'desc') => {
              setOrderColumn(column);
              setOrderDirection(direction);
            }}
          />
        </div>
      </CardContent>
    </Card>
  );
} 