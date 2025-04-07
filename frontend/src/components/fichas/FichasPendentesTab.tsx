import { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { 
  FileText, 
  Code, 
  Link, 
  PlayCircle, 
  Loader2, 
  Search, 
  Filter, 
  RefreshCw,
  AlertTriangle,
  MoreHorizontal
} from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { BadgeStatus } from '@/components/ui/badge-status';
import { SortableTable, Column } from '@/components/ui/SortableTable';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

import fichasPendentesService, { FichaPendente } from '@/services/fichasPendentesService';
import { useFichasPendentes, useExcluirFichaPendente } from '@/hooks/useFichasPendentes';
import { useQueryClient } from '@tanstack/react-query';

// Componente de paginação simplificado
interface SimplePaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function SimplePagination({ currentPage, totalPages, onPageChange }: SimplePaginationProps) {
  return (
    <div className="flex items-center justify-center gap-2 mt-4">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
      >
        Anterior
      </Button>
      
      <span className="text-sm">
        Página {currentPage} de {totalPages}
      </span>
      
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
      >
        Próxima
      </Button>
    </div>
  );
}

export function FichasPendentesTab() {
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [search, setSearch] = useState('');
  const [processado, setProcessado] = useState<boolean | undefined>(undefined);
  const [orderColumn, setOrderColumn] = useState('created_at');
  const [orderDirection, setOrderDirection] = useState<'asc' | 'desc'>('desc');
  
  // Modais
  const [viewDataModal, setViewDataModal] = useState(false);
  const [selectedFicha, setSelectedFicha] = useState<FichaPendente | null>(null);
  const [processarModal, setProcessarModal] = useState(false);
  const [processando, setProcessando] = useState(false);
  const [guiasDisponiveis, setGuiasDisponiveis] = useState<any[]>([]);
  const [selectedGuiaId, setSelectedGuiaId] = useState<string | null>(null);
  const [criarGuia, setCriarGuia] = useState(false);
  const [excluirDialogOpen, setExcluirDialogOpen] = useState(false);
  const [fichaParaExcluir, setFichaParaExcluir] = useState<string | null>(null);

  const queryClient = useQueryClient();
  const excluirFichaMutation = useExcluirFichaPendente();

  // Usar o hook useFichasPendentes para gerenciar o cache dos dados
  const { data: fichasPendentesData, isLoading } = useFichasPendentes({
    offset: (page - 1) * perPage,
    limit: perPage,
    search: search || undefined,
    processado: processado,
    order_column: orderColumn,
    order_direction: orderDirection,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1); // Volta para a primeira página ao pesquisar
  };

  const handleViewData = (ficha: FichaPendente) => {
    setSelectedFicha(ficha);
    setViewDataModal(true);
  };

  const handleViewPdf = (ficha: FichaPendente) => {
    if (ficha.arquivo_url) {
      window.open(ficha.arquivo_url, '_blank');
    } else {
      toast.error('URL do arquivo não disponível');
    }
  };

  const handleProcessar = async (ficha: FichaPendente) => {
    setSelectedFicha(ficha);
    setSelectedGuiaId(null);
    setCriarGuia(false);
    setProcessando(false);
    
    try {
      // Carregar guias disponíveis para seleção
      const guias = await fichasPendentesService.buscarGuiasDisponiveis(ficha.numero_guia);
      setGuiasDisponiveis(guias);
    } catch (error) {
      console.error('Erro ao buscar guias:', error);
      setGuiasDisponiveis([]);
    }
    
    setProcessarModal(true);
  };

  const handleExcluir = (id: string) => {
    setFichaParaExcluir(id);
    setExcluirDialogOpen(true);
  };

  const confirmarExclusao = async () => {
    if (!fichaParaExcluir) return;
    
    try {
      console.log('Iniciando exclusão da ficha:', fichaParaExcluir);
      
      // Fechar o diálogo imediatamente
      setExcluirDialogOpen(false);
      setFichaParaExcluir(null);
      
      // Executar a exclusão na API
      const resultado = await excluirFichaMutation.mutateAsync(fichaParaExcluir);
      console.log('Resultado da exclusão:', resultado);
      
      // Mostrar feedback de sucesso
      toast.success('Ficha pendente excluída com sucesso!');
    } catch (error) {
      console.error('Erro ao excluir ficha pendente:', error);
      // Garantir que o diálogo seja fechado mesmo em caso de erro
      setExcluirDialogOpen(false);
      setFichaParaExcluir(null);
      // Mostrar mensagem de erro
      toast.error('Erro ao excluir ficha pendente');
    }
  };

  const confirmarProcessamento = async () => {
    if (!selectedFicha) return;
    
    if (!criarGuia && (!selectedGuiaId || selectedGuiaId === 'no_guias_found')) {
      toast.error('Selecione uma guia existente ou escolha criar uma nova');
      return;
    }
    
    setProcessando(true);
    
    try {
      const result = await fichasPendentesService.processar(selectedFicha.id, {
        criar_guia: criarGuia,
        guia_id: selectedGuiaId && selectedGuiaId !== 'no_guias_found' ? selectedGuiaId : undefined,
      });
      
      if (result.success) {
        toast.success('Ficha processada com sucesso!');
        setProcessarModal(false);
        
        // Resetar o filtro de processado para undefined para mostrar todas as fichas
        setProcessado(undefined);
        
        // Invalidar a query para forçar uma atualização dos dados
        queryClient.invalidateQueries({ queryKey: ['fichas-pendentes'] });
        // Também invalidar a query de fichas para atualizar a outra aba
        queryClient.invalidateQueries({ queryKey: ['fichas'] });
        
        // Forçar uma atualização imediata
        setTimeout(() => {
          queryClient.refetchQueries({ queryKey: ['fichas-pendentes'] });
          queryClient.refetchQueries({ queryKey: ['fichas'] });
        }, 300);
      } else {
        toast.error(result.message || 'Erro ao processar ficha');
      }
    } catch (error: any) {
      console.error('Erro ao processar ficha:', error);
      toast.error(error.message || 'Erro ao processar ficha');
    } finally {
      setProcessando(false);
    }
  };

  const formatarData = (dataString: string | null | undefined) => {
    if (!dataString) return '-';
    try {
      return format(new Date(dataString), 'dd/MM/yyyy');
    } catch (e) {
      return dataString;
    }
  };

  const formatarDataHora = (dataString: string | null | undefined) => {
    if (!dataString) return '-';
    try {
      return format(new Date(dataString), 'dd/MM/yyyy HH:mm');
    } catch (e) {
      return dataString;
    }
  };

  // Definição das colunas para o SortableTable
  const columns: Column<FichaPendente>[] = [
    {
      key: "status",
      label: "Status",
      render: (value: unknown) => {
        const status = value as string;
        return <BadgeStatus value={status} />;
      },
      sortable: true,
    },
    {
      key: "codigo_ficha",
      label: "Código",
      sortable: true,
    },
    {
      key: "numero_guia",
      label: "Guia",
      sortable: true,
    },
    {
      key: "paciente_nome",
      label: "Paciente",
      sortable: true,
    },
    {
      key: "paciente_carteirinha",
      label: "Carteirinha",
      sortable: true,
    },
    {
      key: "data_atendimento",
      label: "Data Atendimento",
      render: (value: unknown) => formatarData(value as string),
      sortable: true,
    },
    {
      key: "total_sessoes",
      label: "Sessões",
      render: (value: unknown) => value ? value.toString() : '0',
      sortable: true,
    },
    {
      key: "created_at",
      label: "Data Upload",
      render: (value: unknown) => formatarDataHora(value as string),
      sortable: true,
    },
    {
      key: "actions",
      label: "Ações",
      render: (_: unknown, ficha: FichaPendente) => {
        return (
          <div className="flex justify-center">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Abrir menu</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleViewPdf(ficha)}>
                  Visualizar PDF
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleViewData(ficha)}>
                  Visualizar Dados
                </DropdownMenuItem>
                {!ficha.processado && (
                  <DropdownMenuItem onClick={() => handleProcessar(ficha)}>
                    Processar Ficha
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem 
                  onClick={() => handleExcluir(ficha.id)}
                  className="text-red-600"
                >
                  Excluir
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        );
      }
    }
  ];

  // Função para lidar com a ordenação
  const handleSort = (column: string, direction: 'asc' | 'desc') => {
    setOrderColumn(column);
    setOrderDirection(direction);
    setPage(1);
  };

  // Calcular o total de páginas
  const totalPages = Math.ceil((fichasPendentesData?.total || 0) / perPage);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between gap-2">
        <form onSubmit={handleSearch} className="flex gap-2 flex-1">
          <Input
            placeholder="Buscar por nome, carteirinha ou código..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-sm"
          />
          <Button type="submit" size="icon" variant="outline">
            <Search className="h-4 w-4" />
          </Button>
          <Button 
            type="button" 
            size="icon" 
            variant="outline"
            onClick={() => {
              setSearch('');
              setProcessado(undefined);
              setPage(1);
              queryClient.invalidateQueries({ queryKey: ['fichas-pendentes'] });
            }}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </form>
        
        <div className="flex gap-2">
          <Select value={processado === undefined ? 'todos' : processado ? 'importado' : 'pendente'} 
                 onValueChange={(value) => {
            if (value === 'todos') {
              setProcessado(undefined);
            } else if (value === 'importado') {
              setProcessado(true);
            } else {
              setProcessado(false);
            }
            setPage(1);
          }}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filtrar por status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="todos">Todos</SelectItem>
              <SelectItem value="pendente">Não importados</SelectItem>
              <SelectItem value="importado">Importados</SelectItem>
            </SelectContent>
          </Select>
          
          <Button 
            onClick={() => queryClient.invalidateQueries({ queryKey: ['fichas-pendentes'] })} 
            variant="outline"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filtrar
          </Button>
        </div>
      </div>
      
      <SortableTable
        key={`fichas-pendentes-${page}-${perPage}-${orderColumn}-${orderDirection}`}
        data={fichasPendentesData?.items || []}
        columns={columns}
        loading={isLoading}
        onSort={handleSort}
        sortable={true}
        pageCount={totalPages}
        pageIndex={page - 1}
        pageSize={perPage}
        totalRecords={fichasPendentesData?.total || 0}
        onPageChange={(newPage) => {
          setPage(newPage + 1);
        }}
        onPageSizeChange={(newSize) => {
          setPerPage(newSize);
          setPage(1);
        }}
      />
      
      {/* Modal para visualizar dados */}
      <Dialog open={viewDataModal} onOpenChange={setViewDataModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Dados Extraídos da Ficha</DialogTitle>
            <DialogDescription>
              Detalhes extraídos do PDF para a ficha {selectedFicha?.codigo_ficha}
            </DialogDescription>
          </DialogHeader>
          
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Dados Básicos</h3>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-muted-foreground">Código da Ficha</p>
                <p>{selectedFicha?.codigo_ficha || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Número da Guia</p>
                <p>{selectedFicha?.numero_guia || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Paciente</p>
                <p>{selectedFicha?.paciente_nome || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Carteirinha</p>
                <p>{selectedFicha?.paciente_carteirinha || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Data Atendimento</p>
                <p>{formatarData(selectedFicha?.data_atendimento)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Sessões</p>
                <p>{selectedFicha?.total_sessoes || '-'}</p>
              </div>
            </div>
            
            <h3 className="font-semibold mb-2">Dados Completos (JSON)</h3>
            <pre className="bg-muted p-4 rounded-md overflow-x-auto text-xs">
              {JSON.stringify(selectedFicha?.dados_extraidos || {}, null, 2)}
            </pre>
            
            <h3 className="font-semibold mb-2 mt-4">Observações</h3>
            <p className="text-sm">{selectedFicha?.observacoes || 'Nenhuma observação'}</p>
          </div>
          
          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setViewDataModal(false)}>
              Fechar
            </Button>
            {selectedFicha && !selectedFicha.processado && (
              <Button onClick={() => {
                setViewDataModal(false);
                setTimeout(() => handleProcessar(selectedFicha), 100);
              }}>
                Processar Ficha
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Modal para processar ficha */}
      <Dialog open={processarModal} onOpenChange={setProcessarModal}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Processar Ficha Pendente</DialogTitle>
            <DialogDescription>
              Escolha como deseja processar a ficha {selectedFicha?.codigo_ficha}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="flex items-center space-x-2">
              <input
                type="radio"
                id="vincular-guia"
                checked={!criarGuia}
                onChange={() => setCriarGuia(false)}
                className="h-4 w-4"
              />
              <label htmlFor="vincular-guia" className="text-sm font-medium">
                Vincular a uma guia existente
              </label>
            </div>
            
            {!criarGuia && (
              <div className="pl-6">
                <Select value={selectedGuiaId || ''} onValueChange={setSelectedGuiaId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione uma guia" />
                  </SelectTrigger>
                  <SelectContent>
                    {guiasDisponiveis.length === 0 ? (
                      <SelectItem value="no_guias_found" disabled>
                        Nenhuma guia encontrada
                      </SelectItem>
                    ) : (
                      guiasDisponiveis.map((guia) => (
                        <SelectItem key={guia.id} value={guia.id}>
                          {guia.numero_guia} - {guia.paciente_nome || 'Sem nome'}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
                
                {guiasDisponiveis.length === 0 && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Nenhuma guia encontrada com o número {selectedFicha?.numero_guia}
                  </p>
                )}
              </div>
            )}
            
            <div className="flex items-center space-x-2">
              <input
                type="radio"
                id="criar-guia"
                checked={criarGuia}
                onChange={() => setCriarGuia(true)}
                className="h-4 w-4"
              />
              <label htmlFor="criar-guia" className="text-sm font-medium">
                Criar uma nova guia automaticamente
              </label>
            </div>
            
            {criarGuia && (
              <div className="pl-6">
                <p className="text-sm text-muted-foreground">
                  Uma nova guia será criada com os dados extraídos do PDF.
                  Certifique-se de que o paciente e a carteirinha existem no sistema.
                </p>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setProcessarModal(false)} disabled={processando}>
              Cancelar
            </Button>
            <Button onClick={confirmarProcessamento} disabled={processando}>
              {processando ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processando...
                </>
              ) : (
                'Confirmar'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Dialog de confirmação de exclusão */}
      <AlertDialog 
        open={excluirDialogOpen} 
        onOpenChange={(open: boolean) => {
          if (!open) {
            // Limpar o estado quando o diálogo for fechado
            setFichaParaExcluir(null);
          }
          // Atualizar o estado do diálogo
          setExcluirDialogOpen(open);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir esta ficha pendente? Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => {
              // Garantir que o estado seja limpo ao cancelar
              setFichaParaExcluir(null);
              setExcluirDialogOpen(false);
            }}>
              Cancelar
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={(e: React.MouseEvent) => {
                e.preventDefault();
                confirmarExclusao();
              }}
              className="bg-red-600 hover:bg-red-700"
            >
              {excluirFichaMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Excluindo...
                </>
              ) : (
                'Excluir'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
} 