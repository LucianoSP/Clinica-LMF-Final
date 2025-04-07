import { Carteirinha, CarteirinhaStatus } from '@/types/carteirinha';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye, FileDown, Plus } from 'lucide-react';
import { BadgeCarteirinhaStatus } from '@/components/ui/badge-carteirinha-status';
import { SortableTable, Column } from '@/components/ui/SortableTable';
import { formatarData } from '@/lib/utils';
import { useState } from 'react';
import { Input } from '@/components/ui/input';

interface PacienteCarteirinhasProps {
  carteirinhas?: Carteirinha[];
  onViewCarteirinha: (carteirinha: Carteirinha) => void;
}

export function PacienteCarteirinhas({ 
  carteirinhas = [],
  onViewCarteirinha 
}: PacienteCarteirinhasProps) {
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [orderColumn, setOrderColumn] = useState('validade');
  const [orderDirection, setOrderDirection] = useState<'asc' | 'desc'>('desc');

  const columns: Column<Carteirinha>[] = [
    {
      key: 'numero_carteirinha',
      label: 'Número',
      render: (value) => value?.toString() || 'N/A',
    },
    {
      key: 'plano_saude_nome',
      label: 'Plano de Saúde',
      render: (value) => value?.toString() || 'N/A',
    },
    {
      key: 'data_validade',
      label: 'Validade',
      render: (value) => formatarData(value?.toString()),
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => {
        const status = value?.toString().toLowerCase() as CarteirinhaStatus;
        return <BadgeCarteirinhaStatus value={status} />;
      },
    },
    {
      key: 'actions',
      label: 'Ações',
      render: (_, item) => (
        <Button variant="ghost" size="sm" onClick={() => onViewCarteirinha(item)}>
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ];

  const filteredData = carteirinhas.filter(carteirinha => 
    carteirinha.numero_carteirinha?.toLowerCase().includes(search.toLowerCase()) ||
    carteirinha.status?.toLowerCase().includes(search.toLowerCase()) ||
    carteirinha.plano_saude_nome?.toLowerCase().includes(search.toLowerCase())
  );

  const paginatedData = filteredData.slice((page - 1) * perPage, page * perPage);
  const totalPages = Math.ceil(filteredData.length / perPage);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Carteirinhas</CardTitle>
          <div className="flex gap-2">
            <Button 
              variant="outline"
              className="bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
            >
              <Plus className="mr-2 h-4 w-4" />
              Nova Carteirinha
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center gap-4 mb-4">
          <Input
            placeholder="Buscar carteirinhas..."
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