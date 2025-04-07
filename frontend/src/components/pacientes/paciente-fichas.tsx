import { Ficha, StatusFicha } from '@/types/ficha';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye, FileDown, Plus } from 'lucide-react';
import { BadgeFichaStatus } from '@/components/ui/badge-ficha-status';
import { SortableTable, Column } from '@/components/ui/SortableTable';
import { formatarData } from '@/lib/utils';
import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { FileLink } from '@/components/ui/file-link';
import { QuantidadeProgress } from '@/components/ui/quantidade-progress';
import { useFichasPorPaciente } from '@/hooks/useFichas';

interface PacienteFichasProps {
  pacienteId: string;
  onViewFicha?: (ficha: Ficha) => void;
}

export function PacienteFichas({ pacienteId, onViewFicha }: PacienteFichasProps) {
  const { data: fichasData, isLoading } = useFichasPorPaciente(
    pacienteId,
    1,
    100
  );
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [orderColumn, setOrderColumn] = useState('data_atendimento');
  const [orderDirection, setOrderDirection] = useState<'asc' | 'desc'>('desc');

  if (isLoading) {
    return <div>Carregando fichas...</div>;
  }

  const columns: Column<Ficha>[] = [
    {
      key: 'codigo_ficha',
      label: 'Código',
      render: (value) => value?.toString() || 'N/A',
      sortable: true,
    },
    {
      key: 'numero_guia',
      label: 'Guia',
      render: (value) => value?.toString() || 'N/A',
      sortable: true,
    },
    {
      key: 'paciente_carteirinha',
      label: 'Carteirinha',
      render: (value) => value?.toString() || 'N/A',
      sortable: true,
    },
    {
      key: 'arquivo_digitalizado',
      label: 'Arquivo',
      render: (value) => <FileLink url={value?.toString()} />,
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => {
        const status = value?.toString().toLowerCase() as StatusFicha;
        return <BadgeFichaStatus value={status} />;
      },
      sortable: true,
    },
    {
      key: 'sessoes',
      label: 'Sessões',
      render: (_, item) => (
        <QuantidadeProgress
          autorizada={item.total_sessoes || 0}
          executada={item.sessoes_conferidas || 0}
        />
      ),
    },
    {
      key: 'actions',
      label: 'Ações',
      render: (_, item) => (
        <Button variant="ghost" size="sm" onClick={() => onViewFicha?.(item)}>
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ];

  const filteredData = fichasData?.items.filter(ficha =>
    ficha.codigo_ficha?.toLowerCase().includes(search.toLowerCase()) ||
    ficha.numero_guia?.toLowerCase().includes(search.toLowerCase()) ||
    ficha.paciente_carteirinha?.toLowerCase().includes(search.toLowerCase()) ||
    ficha.status?.toLowerCase().includes(search.toLowerCase())
  ) || [];

  const paginatedData = filteredData.slice((page - 1) * perPage, page * perPage);
  const totalPages = Math.ceil(filteredData.length / perPage);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Fichas</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
            >
              <Plus className="mr-2 h-4 w-4" />
              Nova Ficha
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <Input
              placeholder="Buscar fichas..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="max-w-sm"
            />
          </div>

          <SortableTable<Ficha>
            columns={columns}
            data={paginatedData}
            pageCount={totalPages}
            pageIndex={page - 1}
            pageSize={perPage}
            totalRecords={filteredData.length}
            onPageChange={(newPage) => setPage(newPage + 1)}
            onPageSizeChange={(newSize) => setPerPage(newSize)}
            sortable
            onSort={(column, direction) => {
              setOrderColumn(column);
              setOrderDirection(direction);
            }}
            loading={isLoading}
          />
        </div>
      </CardContent>
    </Card>
  );
}