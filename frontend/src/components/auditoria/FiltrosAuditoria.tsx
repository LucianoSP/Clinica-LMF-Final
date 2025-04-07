import type { FC } from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { X, FileDown, RefreshCcw } from 'lucide-react';
import { TabelaDivergencias } from './TabelaDivergencias';
import { Divergencia } from '@/types/auditoria';

export type FiltrosAuditoriaProps = {
  dataInicial: string | null;
  setDataInicial: (date: string | null) => void;
  dataFinal: string | null;
  setDataFinal: (date: string | null) => void;
  statusFiltro: string;
  setStatusFiltro: (status: string) => void;
  tipoDivergencia: string;
  setTipoDivergencia: (tipo: string) => void;
  prioridade: string;
  setPrioridade: (prioridade: string) => void;
  onAuditoria: () => Promise<void>;
  onGerarRelatorio: () => Promise<void>;
  loading: boolean;
  divergencias: Divergencia[];
  onMarcarResolvido: (id: string) => void;
  pageCount: number;
  pageIndex: number;
  pageSize: number;
  totalRecords: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newSize: number) => void;
};

const tiposDivergencia = [
  { value: 'todos', label: 'Todos os tipos' },
  { value: 'execucao_sem_ficha', label: 'Execução sem Ficha' },
  { value: 'ficha_sem_execucao', label: 'Ficha sem Execução' },
  { value: 'sessao_sem_assinatura', label: 'Sessão sem Assinatura' },
  { value: 'data_divergente', label: 'Data Divergente' },
  { value: 'guia_vencida', label: 'Guia Vencida' },
  { value: 'quantidade_excedida', label: 'Quantidade Excedida' },
  { value: 'falta_data_execucao', label: 'Falta Data Execução' },
  { value: 'duplicidade', label: 'Duplicidade' },
] as const;

const statusOptions = [
  { value: 'todos', label: 'Todos os status' },
  { value: 'pendente', label: 'Pendente' },
  { value: 'resolvida', label: 'Resolvida' },
] as const;

const prioridadeOptions = [
  { value: 'todas', label: 'Todas as prioridades' },
  { value: 'ALTA', label: 'Alta' },
  { value: 'MEDIA', label: 'Média' },
] as const;

const FiltrosAuditoria: FC<FiltrosAuditoriaProps> = ({
  dataInicial,
  setDataInicial,
  dataFinal,
  setDataFinal,
  statusFiltro,
  setStatusFiltro,
  tipoDivergencia,
  setTipoDivergencia,
  prioridade,
  setPrioridade,
  onAuditoria,
  onGerarRelatorio,
  loading,
  divergencias,
  onMarcarResolvido,
  pageCount,
  pageIndex,
  pageSize,
  totalRecords,
  onPageChange,
  onPageSizeChange
}) => {
  const limparFiltros = () => {
    setDataInicial(null);
    setDataFinal(null);
    setStatusFiltro('todos');
    setTipoDivergencia('todos');
    setPrioridade('todas');
  };

  return (
    <div className="border border-gray-200 rounded-lg shadow-sm bg-white">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Filtros</h2>
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={onGerarRelatorio}
              disabled={loading}
              className="flex items-center"
            >
              <FileDown className="w-4 h-4 mr-2" />
              Exportar
            </Button>
            <Button
              variant="outline"
              onClick={onAuditoria}
              disabled={loading}
              className="flex items-center bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-600 transition-colors"
            >
              <RefreshCcw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="flex flex-col">
            <Label className="mb-2">Data Inicial</Label>
            <Input
              type="date"
              value={dataInicial || ''}
              onChange={(e) => setDataInicial(e.target.value || null)}
            />
          </div>

          <div className="flex flex-col">
            <Label className="mb-2">Data Final</Label>
            <Input
              type="date"
              value={dataFinal || ''}
              onChange={(e) => setDataFinal(e.target.value || null)}
            />
          </div>

          <div className="flex flex-col">
            <Label className="mb-2">Status</Label>
            <Select value={statusFiltro} onValueChange={setStatusFiltro}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione o status" />
              </SelectTrigger>
              <SelectContent>
                {statusOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col">
            <Label className="mb-2">Tipo de Divergência</Label>
            <Select value={tipoDivergencia} onValueChange={setTipoDivergencia}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                {tiposDivergencia.map(tipo => (
                  <SelectItem key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col relative">
            <Label className="mb-2">Prioridade</Label>
            <div className="flex gap-2">
              <div className="flex-1">
                <Select value={prioridade} onValueChange={setPrioridade}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a prioridade" />
                  </SelectTrigger>
                  <SelectContent>
                    {prioridadeOptions.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={limparFiltros}
                className="h-10 w-10 text-gray-500 hover:text-gray-700"
                title="Limpar Filtros"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <TabelaDivergencias
          divergencias={divergencias}
          onMarcarResolvido={onMarcarResolvido}
          loading={loading}
          pageCount={pageCount}
          pageIndex={pageIndex}
          pageSize={pageSize}
          totalRecords={totalRecords}
          onPageChange={onPageChange}
          onPageSizeChange={onPageSizeChange}
        />
      </div>
    </div>
  );
};

export default FiltrosAuditoria;