import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { formatarData } from "@/lib/utils";
import { parse } from 'date-fns';
import { DivergenciaBadge } from "../ui/divergencia-badge";
import { StatusBadge } from "../ui/status-badge";
import { Button } from "@/components/ui/button";
import { Divergencia } from "@/types/auditoria";
import { CheckCircle2, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface DetalheDivergenciaProps {
  divergencia: Divergencia | null;
  open: boolean;
  onClose: () => void;
  onResolverClick: () => void;
}

export function DetalheDivergencia({ divergencia, open, onClose, onResolverClick }: DetalheDivergenciaProps) {
  if (!divergencia) return null;

  // Função para renderizar o badge de prioridade
  const renderizarPrioridade = (prioridade: string): JSX.Element => {
    const prioridadeUpper = prioridade.toUpperCase();
    
    const classesPrioridade: Record<string, string> = {
      'ALTA': 'bg-red-50 text-red-700 border-red-100',
      'MEDIA': 'bg-yellow-50 text-yellow-700 border-yellow-100',
      'BAIXA': 'bg-blue-50 text-blue-700 border-blue-100'
    };
    
    return (
      <span className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold",
        classesPrioridade[prioridadeUpper] || 'bg-gray-50 text-gray-700 border-gray-100'
      )}>
        {prioridadeUpper === 'ALTA' ? 'Alta' : prioridadeUpper === 'MEDIA' ? 'Média' : prioridadeUpper === 'BAIXA' ? 'Baixa' : prioridade}
      </span>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl bg-white">
        <DialogHeader className="border-b pb-4">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl font-semibold text-gray-800">
              Detalhes da Divergência
            </DialogTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div className="grid grid-cols-4 gap-6">
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">ID da Sessão</h4>
              <p className="mt-1 text-gray-800 font-medium">
                {divergencia.sessao_id || divergencia.detalhes?.sessao_id || 'Não informado'}
              </p>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Guia</h4>
              <p className="mt-1 text-gray-800 font-medium">{divergencia.numero_guia}</p>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Paciente</h4>
              <p className="mt-1 text-gray-800 font-medium">{divergencia.paciente_nome || 'Não informado'}</p>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Carteirinha</h4>
              <p className="mt-1 text-gray-800 font-medium">{divergencia.carteirinha || 'Não informado'}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Data do Atendimento</h4>
              <p className="mt-1 text-gray-800 font-medium">
                {(() => {
                  if (!divergencia.data_atendimento) return 'Não informado';
                  try {
                    const date = divergencia.data_atendimento.includes('/') 
                      ? new Date(divergencia.data_atendimento.split('/').reverse().join('-'))
                      : new Date(divergencia.data_atendimento);
                    return formatarData(date);
                  } catch {
                    return 'Não informado';
                  }
                })()} 
              </p>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Data da Execução</h4>
              <p className="mt-1 text-gray-800 font-medium">
                {(() => {
                  if (!divergencia.data_execucao) return 'Não informado';
                  try {
                    const date = divergencia.data_execucao.includes('/') 
                      ? new Date(divergencia.data_execucao.split('/').reverse().join('-'))
                      : new Date(divergencia.data_execucao);
                    return formatarData(date);
                  } catch {
                    return 'Não informado';
                  }
                })()} 
              </p>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Data de Identificação</h4>
              <p className="mt-1 text-gray-800 font-medium">
                {(() => {
                  if (!divergencia.data_identificacao) return 'Não informado';
                  try {
                    const date = divergencia.data_identificacao.includes('/') 
                      ? new Date(divergencia.data_identificacao.split('/').reverse().join('-'))
                      : new Date(divergencia.data_identificacao);
                    return formatarData(date);
                  } catch {
                    return 'Não informado';
                  }
                })()} 
              </p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-6">
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Tipo de Divergência</h4>
              <p className="mt-1 text-gray-800 font-medium">
                {(() => {
                  const tipoValue = String(divergencia.tipo || divergencia.tipo_divergencia || '');
                  const tiposFormatados: Record<string, string> = {
                    'execucao_sem_ficha': 'Execução sem Ficha',
                    'ficha_sem_execucao': 'Ficha sem Execução',
                    'sessao_sem_assinatura': 'Sessão sem Assinatura',
                    'data_divergente': 'Data Divergente',
                    'guia_vencida': 'Guia Vencida',
                    'quantidade_excedida': 'Quantidade Excedida',
                    'falta_data_execucao': 'Falta Data Execução',
                    'duplicidade': 'Duplicidade'
                  };
                  return tiposFormatados[tipoValue] || tipoValue.charAt(0).toUpperCase() + tipoValue.slice(1).replace(/_/g, ' ');
                })()}
              </p>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Status</h4>
              <div className="mt-1">
                <StatusBadge status={divergencia.status} />
              </div>
            </div>
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Prioridade</h4>
              <div className="mt-1">
                {renderizarPrioridade(divergencia.prioridade || 'MEDIA')}
              </div>
            </div>
          </div>

          <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
            <h4 className="text-sm font-medium text-gray-500">Descrição</h4>
            <p className="mt-1 text-gray-800">{divergencia.descricao || 'Não informado'}</p>
          </div>

          {divergencia.detalhes?.observacoes && (
            <div className="bg-gray-50/50 p-4 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-sm font-medium text-gray-500">Observações</h4>
              <p className="mt-1 text-gray-800">{divergencia.detalhes.observacoes}</p>
            </div>
          )}
        </div>

        <DialogFooter className="border-t pt-4">
          <div className="flex justify-between w-full">
            <Button variant="outline" onClick={onClose}>
              Fechar
            </Button>
            {divergencia.status !== 'resolvido' && (
              <Button
                onClick={onResolverClick}
                className="bg-emerald-600 hover:bg-emerald-700 text-white"
                size="lg"
              >
                <CheckCircle2 className="mr-2 h-5 w-5" />
                Marcar como Resolvida
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
