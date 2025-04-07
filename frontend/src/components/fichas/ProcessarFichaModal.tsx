import { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { formatarData } from '@/lib/utils';
import { Ficha } from "@/types/ficha";
import { useToast } from '@/hooks/use-toast';
import { useSessoes, useAtualizarSessao } from '@/hooks/useSessoes';
import { Sessao } from '@/types/sessao';
import { AlertCircle, Plus } from 'lucide-react';
import { api } from '@/services/api';

interface ProcessarFichaModalProps {
  ficha: Ficha | null;
  isOpen: boolean;
  onClose: () => void;
  onProcessar: (ficha: Ficha) => void;
}

export function ProcessarFichaModal({ 
  ficha, 
  isOpen, 
  onClose, 
  onProcessar 
}: ProcessarFichaModalProps) {
  const [sessoes, setSessoes] = useState<Sessao[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGerandoSessoes, setIsGerandoSessoes] = useState(false);
  const { toast } = useToast();
  
  // Carregar as sessões da ficha
  const { data: sessoesData, isLoading: isLoadingSessoes, error: sessoesError, refetch: refetchSessoes } = useSessoes(isOpen ? ficha?.id || null : null);
  const { mutateAsync: atualizarSessao } = useAtualizarSessao();

  useEffect(() => {
    if (ficha && isOpen && sessoesData?.items) {
      setSessoes(sessoesData.items);
    }
  }, [ficha, isOpen, sessoesData]);

  const handleSessaoChange = (index: number, field: keyof Sessao, value: any) => {
    const novasSessoes = [...sessoes];
    novasSessoes[index] = {
      ...novasSessoes[index],
      [field]: value
    };
    setSessoes(novasSessoes);
  };

  const handleSalvar = async () => {
    if (!ficha) return;
    
    setIsLoading(true);
    try {
      // Salvar cada sessão
      for (const sessao of sessoes) {
        await atualizarSessao({
          fichaId: ficha.id,
          sessaoId: sessao.id,
          dados: sessao
        });
      }
      
      toast({
        title: "Sucesso",
        description: "Sessões salvas com sucesso"
      });
      
      onProcessar(ficha);
    } catch (error) {
      toast({
        title: "Erro",
        description: "Ocorreu um erro ao salvar as sessões",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
      onClose();
    }
  };

  const handleGerarSessoes = async () => {
    if (!ficha) return;
    
    setIsGerandoSessoes(true);
    try {
      await api.post(`/api/fichas/${ficha.id}/gerar-sessoes`);
      
      toast({
        title: "Sucesso",
        description: "Sessões geradas com sucesso"
      });
      
      // Recarregar as sessões
      await refetchSessoes();
    } catch (error) {
      toast({
        title: "Erro",
        description: "Ocorreu um erro ao gerar as sessões",
        variant: "destructive"
      });
    } finally {
      setIsGerandoSessoes(false);
    }
  };

  // Verifica se houve um erro 404, indicando que a API não existe
  const isAPIUnavailable = sessoesError && 
    (sessoesError as any)?.response?.status === 404;

  // Verifica se o número de sessões é menor que o total_sessoes da ficha
  const precisaGerarSessoes = ficha && 
    (!sessoes.length || (ficha.total_sessoes && sessoes.length < ficha.total_sessoes));

  if (!ficha) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Processar Ficha</DialogTitle>
          <DialogDescription>
            Edite os dados de cada sessão para a ficha {ficha.codigo_ficha}
          </DialogDescription>
        </DialogHeader>
        
        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-muted-foreground">Código da Ficha</p>
              <p className="font-medium">{ficha.codigo_ficha}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Número da Guia</p>
              <p className="font-medium">{ficha.numero_guia}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Paciente</p>
              <p className="font-medium">{ficha.paciente_nome}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Carteirinha</p>
              <p className="font-medium">{ficha.paciente_carteirinha}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Data Atendimento</p>
              <p className="font-medium">{formatarData(ficha.data_atendimento)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Sessões</p>
              <p className="font-medium">{ficha.total_sessoes || 0}</p>
            </div>
            {ficha.arquivo_digitalizado && (
              <div className="col-span-full mt-2">
                <p className="text-sm text-muted-foreground">Arquivo Digitalizado</p>
                <a 
                  href={ficha.arquivo_digitalizado} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                >
                  Visualizar PDF
                </a>
              </div>
            )}
          </div>
          
          {isAPIUnavailable ? (
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-md">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-yellow-500 mr-2" />
                <p className="text-sm text-yellow-700">
                  <span className="font-bold">API indisponível:</span> O endpoint para gerenciar sessões ainda não está implementado no backend.
                </p>
              </div>
              <p className="text-sm text-yellow-700 mt-2">
                Entre em contato com o time de desenvolvimento para implementar os endpoints necessários:
              </p>
              <ul className="list-disc list-inside text-sm text-yellow-700 mt-1 ml-2">
                <li><code className="bg-yellow-100 px-1 rounded">/api/fichas/{'{ficha_id}'}/sessoes</code> - Listar sessões</li>
                <li><code className="bg-yellow-100 px-1 rounded">/api/fichas/{'{ficha_id}'}/sessoes/{'{sessao_id}'}</code> - Atualizar sessão</li>
              </ul>
            </div>
          ) : isLoadingSessoes ? (
            <div className="flex justify-center py-6">
              <span>Carregando sessões...</span>
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Sessões</h3>
                {precisaGerarSessoes && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleGerarSessoes} 
                    disabled={isGerandoSessoes}
                    className="flex items-center gap-1"
                  >
                    <Plus className="h-4 w-4" />
                    {isGerandoSessoes ? "Gerando..." : "Gerar Sessões"}
                  </Button>
                )}
              </div>
              
              {sessoes.length === 0 ? (
                <div className="border rounded-md p-6 text-center">
                  <p className="text-muted-foreground mb-4">Nenhuma sessão encontrada para esta ficha.</p>
                  <Button 
                    variant="outline" 
                    onClick={handleGerarSessoes} 
                    disabled={isGerandoSessoes}
                    className="flex items-center gap-1"
                  >
                    <Plus className="h-4 w-4" />
                    {isGerandoSessoes ? "Gerando..." : "Gerar Sessões"}
                  </Button>
                </div>
              ) : (
                <div className="border rounded-md">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ordem</TableHead>
                        <TableHead>Data da Sessão</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-center">Assinado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sessoes.map((sessao, index) => (
                        <TableRow key={sessao.id}>
                          <TableCell>{sessao.ordem_execucao || index + 1}</TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              <Input
                                type="date"
                                value={sessao.data_sessao ? sessao.data_sessao.substring(0, 10) : ''}
                                onChange={(e) => handleSessaoChange(
                                  index, 
                                  'data_sessao', 
                                  e.target.value
                                )}
                              />
                            </div>
                          </TableCell>
                          <TableCell>
                            <Select
                              value={sessao.status}
                              onValueChange={(value) => handleSessaoChange(index, 'status', value)}
                            >
                              <SelectTrigger className="w-full">
                                <SelectValue placeholder="Selecione o status" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="pendente">Pendente</SelectItem>
                                <SelectItem value="realizada">Realizada</SelectItem>
                                <SelectItem value="cancelada">Cancelada</SelectItem>
                                <SelectItem value="faturada">Faturada</SelectItem>
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell className="text-center">
                            <Switch 
                              checked={sessao.possui_assinatura} 
                              onCheckedChange={(value) => handleSessaoChange(
                                index, 
                                'possui_assinatura', 
                                value
                              )}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </>
          )}
        </div>
        
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Fechar
          </Button>
          {!isAPIUnavailable && sessoes.length > 0 && (
            <Button onClick={handleSalvar} disabled={isLoading || isLoadingSessoes}>
              {isLoading ? "Salvando..." : "Salvar Alterações"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 