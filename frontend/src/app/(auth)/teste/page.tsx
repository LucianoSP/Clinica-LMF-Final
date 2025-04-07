"use client"

import React, { useState, useEffect } from 'react';
import { Search, Calendar, Check, X, Link, Filter, AlertCircle, Clock, Trash } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useToast } from "@/components/ui/use-toast";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

// Interfaces para tipagem
interface Sessao {
  id: string;
  ficha_id: string;
  guia_id: string;
  data_sessao: string;
  possui_assinatura: boolean;
  numero_guia: string;
  codigo_ficha: string;
  ordem_execucao: number;
}

interface Execucao {
  id: string;
  guia_id: string;
  sessao_id: string | null;
  data_execucao: string;
  numero_guia: string;
  codigo_ficha: string;
  codigo_ficha_temp: boolean;
  origem: string;
  paciente_nome: string;
  paciente_carteirinha: string;
  profissional_executante: string;
  ordem_execucao: number | null;
}

interface Filtros {
  search: string;
  guideNumber: string;
  showLinked: boolean;
  showUnlinked: boolean;
}

// Dados de exemplo - em uma implementação real, seriam buscados da API
const mockSessions: Sessao[] = [
  { id: '1', ficha_id: 'F123', guia_id: 'G1', data_sessao: '2025-03-18', possui_assinatura: true, numero_guia: '60354715', codigo_ficha: 'FICHA001', ordem_execucao: 1 },
  { id: '2', ficha_id: 'F123', guia_id: 'G1', data_sessao: '2025-03-18', possui_assinatura: true, numero_guia: '60354715', codigo_ficha: 'FICHA001', ordem_execucao: 2 },
  { id: '3', ficha_id: 'F123', guia_id: 'G1', data_sessao: '2025-03-19', possui_assinatura: true, numero_guia: '60354715', codigo_ficha: 'FICHA001', ordem_execucao: 3 },
  { id: '4', ficha_id: 'F124', guia_id: 'G2', data_sessao: '2025-03-17', possui_assinatura: true, numero_guia: '60354716', codigo_ficha: 'FICHA002', ordem_execucao: 1 },
  { id: '5', ficha_id: 'F125', guia_id: 'G3', data_sessao: '2025-03-15', possui_assinatura: false, numero_guia: '60354717', codigo_ficha: 'FICHA003', ordem_execucao: 1 },
];

const mockExecutions: Execucao[] = [
  { id: 'E1', guia_id: 'G1', sessao_id: null, data_execucao: '2025-03-18', numero_guia: '60354715', codigo_ficha: 'TEMP_60354715_20250318_1', codigo_ficha_temp: true, origem: 'unimed_scraping', paciente_nome: 'João Silva', paciente_carteirinha: '12345678', profissional_executante: 'Dr. Carlos Mendes', ordem_execucao: 1 },
  { id: 'E2', guia_id: 'G1', sessao_id: null, data_execucao: '2025-03-18', numero_guia: '60354715', codigo_ficha: 'TEMP_60354715_20250318_2', codigo_ficha_temp: true, origem: 'unimed_scraping', paciente_nome: 'João Silva', paciente_carteirinha: '12345678', profissional_executante: 'Dr. Carlos Mendes', ordem_execucao: 2 },
  { id: 'E3', guia_id: 'G1', sessao_id: null, data_execucao: '2025-03-19', numero_guia: '60354715', codigo_ficha: 'TEMP_60354715_20250319_1', codigo_ficha_temp: true, origem: 'unimed_scraping', paciente_nome: 'João Silva', paciente_carteirinha: '12345678', profissional_executante: 'Dr. Carlos Mendes', ordem_execucao: 3 },
  { id: 'E4', guia_id: 'G2', sessao_id: null, data_execucao: '2025-03-17', numero_guia: '60354716', codigo_ficha: 'TEMP_60354716_20250317_1', codigo_ficha_temp: true, origem: 'unimed_scraping', paciente_nome: 'Maria Oliveira', paciente_carteirinha: '87654321', profissional_executante: 'Dra. Ana Paula Santos', ordem_execucao: 1 },
  { id: 'E5', guia_id: 'G3', sessao_id: '5', data_execucao: '2025-03-15', numero_guia: '60354717', codigo_ficha: 'FICHA003', codigo_ficha_temp: false, origem: 'unimed_scraping', paciente_nome: 'Pedro Costa', paciente_carteirinha: '23456789', profissional_executante: 'Dr. Lucas Ferreira', ordem_execucao: 1 },
];

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

const SessionLinkingInterface = () => {
  const { toast } = useToast();
  
  // Gerenciamento de estado
  const [sessions, setSessions] = useState<Sessao[]>(mockSessions);
  const [executions, setExecutions] = useState<Execucao[]>(mockExecutions);
  const [selectedSession, setSelectedSession] = useState<Sessao | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<Execucao | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState<boolean>(false);
  const [filters, setFilters] = useState<Filtros>({
    search: '',
    guideNumber: '',
    showLinked: true,
    showUnlinked: true
  });

  // Aplicar filtros aos dados
  const filteredSessions = sessions.filter(session => {
    const matchesSearch = 
      session.numero_guia.includes(filters.search) || 
      session.codigo_ficha.includes(filters.search);
    
    const matchesGuide = filters.guideNumber === "all" || filters.guideNumber === "" ? true : session.numero_guia === filters.guideNumber;
    
    return matchesSearch && matchesGuide;
  });

  const filteredExecutions = executions.filter(execution => {
    const isLinked = execution.sessao_id !== null;
    const showBasedOnLinkStatus = 
      (isLinked && filters.showLinked) || 
      (!isLinked && filters.showUnlinked);
    
    const matchesSearch = 
      execution.numero_guia.includes(filters.search) || 
      execution.codigo_ficha.includes(filters.search) ||
      (execution.paciente_nome && execution.paciente_nome.toLowerCase().includes(filters.search.toLowerCase()));
    
    const matchesGuide = filters.guideNumber === "all" || filters.guideNumber === "" ? true : execution.numero_guia === filters.guideNumber;
    
    return showBasedOnLinkStatus && matchesSearch && matchesGuide;
  });

  // Sugestões inteligentes - encontrar correspondências potenciais entre sessões e execuções
  const getSuggestedMatch = (session: Sessao): Execucao | undefined => {
    return executions.find(execution => 
      execution.sessao_id === null && 
      execution.numero_guia === session.numero_guia && 
      execution.data_execucao === session.data_sessao &&
      execution.ordem_execucao === session.ordem_execucao
    );
  };

  // Vincular uma sessão a uma execução
  const linkSessionToExecution = () => {
    if (!selectedSession || !selectedExecution) return;

    // Em uma implementação real, isso seria uma chamada de API
    const updatedExecutions = executions.map(execution => {
      if (execution.id === selectedExecution.id) {
        return {
          ...execution,
          sessao_id: selectedSession.id,
          codigo_ficha: selectedSession.codigo_ficha,
          codigo_ficha_temp: false
        };
      }
      return execution;
    });

    setExecutions(updatedExecutions);
    setSelectedSession(null);
    setSelectedExecution(null);
    setConfirmDialogOpen(false);

    toast({
      title: "Vinculação Criada com Sucesso",
      description: `Sessão #${selectedSession.id} foi vinculada à execução #${selectedExecution.id}`,
    });
  };

  // Desvincular uma execução de sua sessão
  const unlinkExecution = (executionId: string) => {
    const updatedExecutions = executions.map(execution => {
      if (execution.id === executionId) {
        return {
          ...execution,
          sessao_id: null,
          codigo_ficha: `TEMP_${execution.numero_guia}_${execution.data_execucao.replace(/-/g, '')}_${execution.ordem_execucao || 1}`,
          codigo_ficha_temp: true
        };
      }
      return execution;
    });

    setExecutions(updatedExecutions);
    toast({
      title: "Vinculação Removida",
      description: `Execução #${executionId} foi desvinculada`,
    });
  };

  // Sugerir automaticamente vinculações para todas as sessões não vinculadas
  const autoLinkAll = () => {
    const updatedExecutions = [...executions];
    let linkCount = 0;

    sessions.forEach(session => {
      // Pular se esta sessão já tiver uma execução vinculada
      const alreadyHasLinkedExecution = executions.some(e => e.sessao_id === session.id);
      if (alreadyHasLinkedExecution) return;

      // Encontrar uma execução não vinculada correspondente
      const matchIndex = updatedExecutions.findIndex(e => 
        e.sessao_id === null && 
        e.numero_guia === session.numero_guia && 
        e.data_execucao === session.data_sessao &&
        (e.ordem_execucao === session.ordem_execucao || 
         (e.ordem_execucao === null && session.ordem_execucao !== null))
      );

      if (matchIndex !== -1) {
        updatedExecutions[matchIndex] = {
          ...updatedExecutions[matchIndex],
          sessao_id: session.id,
          codigo_ficha: session.codigo_ficha,
          codigo_ficha_temp: false
        };
        linkCount++;
      }
    });

    if (linkCount > 0) {
      setExecutions(updatedExecutions);
      toast({
        title: "Vinculação Automática Concluída",
        description: `${linkCount} sessões foram vinculadas automaticamente às execuções`,
      });
    } else {
      toast({
        title: "Vinculação Automática",
        description: "Nenhuma nova correspondência foi encontrada para vincular",
      });
    }
  };

  // Lidar com a confirmação de vinculação
  const handleConfirmLink = () => {
    if (selectedSession && selectedExecution) {
      setConfirmDialogOpen(true);
    } else {
      toast({
        title: "Seleção Necessária",
        description: "Por favor, selecione uma sessão e uma execução para vincular",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-3xl font-bold mb-6">Painel de Vinculação de Sessões</h1>
      
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-1">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
            <Input
              placeholder="Buscar por número de guia, código de ficha ou nome do paciente..."
              className="pl-8"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
            />
          </div>
        </div>
        
        <div className="col-span-1">
          <Select
            onValueChange={(value) => setFilters({...filters, guideNumber: value})}
            value={filters.guideNumber}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filtrar por número de guia" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os números de guia</SelectItem>
              {Array.from(new Set(sessions.map(s => s.numero_guia))).map(guideNumber => (
                <SelectItem key={guideNumber} value={guideNumber}>
                  {guideNumber}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => setFilters({
              search: '',
              guideNumber: 'all',
              showLinked: true,
              showUnlinked: true
            })}
            className="flex-1"
          >
            Limpar Filtros
          </Button>
          
          <Button 
            variant="default" 
            onClick={autoLinkAll}
            className="flex-1"
          >
            <Link className="mr-2 h-4 w-4" />
            Vincular Automaticamente
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Painel de Sessões */}
        <Card className="h-[600px] overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
              <CardTitle>Sessões</CardTitle>
              <Badge variant="outline" className="ml-2">{filteredSessions.length}</Badge>
            </div>
            <CardDescription>
              Selecione uma sessão para vincular com uma execução
            </CardDescription>
          </CardHeader>
          <CardContent className="overflow-auto h-full pb-6">
            <div className="space-y-2">
              {filteredSessions.map(session => {
                const suggestedMatch = getSuggestedMatch(session);
                const isSelected = selectedSession?.id === session.id;
                
                return (
                  <Card 
                    key={session.id} 
                    className={`cursor-pointer transition-all ${isSelected ? 'border-primary bg-primary/5' : ''}`}
                    onClick={() => setSelectedSession(session)}
                  >
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold flex items-center">
                            ID Sessão: {session.id}
                            {session.possui_assinatura && 
                              <Badge variant="outline" className="ml-2 bg-green-50 text-green-700 border-green-200">
                                <Check className="h-3 w-3 mr-1" /> Assinada
                              </Badge>
                            }
                          </h3>
                          <p className="text-sm text-gray-500">Ficha: {session.codigo_ficha}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">
                            <Calendar className="h-3 w-3 inline mr-1" /> 
                            {formatDate(session.data_sessao)}
                          </div>
                          <div className="text-xs text-gray-500">
                            Guia: {session.numero_guia}
                          </div>
                        </div>
                      </div>

                      <div className="mt-3 flex justify-between items-center">
                        <div className="text-xs">
                          <Badge variant="outline" className="mr-1">Ordem: {session.ordem_execucao}</Badge>
                        </div>
                        
                        {suggestedMatch && (
                          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                            <Link className="h-3 w-3 mr-1" /> 
                            Correspondência potencial
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}

              {filteredSessions.length === 0 && (
                <div className="py-8 text-center text-gray-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-20" />
                  <p>Nenhuma sessão encontrada com os filtros atuais</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Painel de Execuções */}
        <Card className="h-[600px] overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-center">
              <CardTitle>Execuções</CardTitle>
              <div className="flex gap-2 items-center">
                <div className="text-xs flex items-center gap-1">
                  <input 
                    type="checkbox" 
                    id="showLinked"
                    checked={filters.showLinked}
                    onChange={(e) => setFilters({...filters, showLinked: e.target.checked})}
                  />
                  <label htmlFor="showLinked" className="flex items-center">
                    <Badge variant="outline" className="ml-1 bg-green-50 border-green-200">Vinculadas</Badge>
                  </label>
                </div>
                
                <div className="text-xs flex items-center gap-1">
                  <input 
                    type="checkbox" 
                    id="showUnlinked"
                    checked={filters.showUnlinked}
                    onChange={(e) => setFilters({...filters, showUnlinked: e.target.checked})}
                  />
                  <label htmlFor="showUnlinked" className="flex items-center">
                    <Badge variant="outline" className="ml-1 bg-yellow-50 border-yellow-200">Não Vinculadas</Badge>
                  </label>
                </div>
                
                <Badge variant="outline">{filteredExecutions.length}</Badge>
              </div>
            </div>
            <CardDescription>
              Selecione uma execução não vinculada para vincular com uma sessão
            </CardDescription>
          </CardHeader>
          <CardContent className="overflow-auto h-full pb-6">
            <div className="space-y-2">
              {filteredExecutions.map(execution => {
                const isLinked = execution.sessao_id !== null;
                const isSelected = selectedExecution?.id === execution.id;
                
                return (
                  <Card 
                    key={execution.id} 
                    className={`transition-all ${isLinked ? 'opacity-70' : ''} ${isSelected ? 'border-primary bg-primary/5' : ''}`}
                    onClick={() => !isLinked && setSelectedExecution(execution)}
                  >
                    <CardContent className={`p-4 ${isLinked ? 'cursor-default' : 'cursor-pointer'}`}>
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-semibold flex items-center">
                            ID Execução: {execution.id.substring(0, 8)}
                            {isLinked ? (
                              <Badge className="ml-2 bg-green-50 text-green-700 border-green-200">
                                <Check className="h-3 w-3 mr-1" /> Vinculada à Sessão #{execution.sessao_id}
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="ml-2 bg-yellow-50 text-yellow-700 border-yellow-200">
                                <AlertCircle className="h-3 w-3 mr-1" /> Não Vinculada
                              </Badge>
                            )}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {execution.codigo_ficha_temp ? 'Código Temporário: ' : 'Ficha: '}
                            {execution.codigo_ficha}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium">
                            <Calendar className="h-3 w-3 inline mr-1" /> 
                            {formatDate(execution.data_execucao)}
                          </div>
                          <div className="text-xs text-gray-500">
                            Guia: {execution.numero_guia}
                          </div>
                        </div>
                      </div>

                      <div className="mt-2 text-sm">
                        <p className="truncate">Paciente: {execution.paciente_nome}</p>
                        <p className="text-gray-500 text-xs">Profissional: {execution.profissional_executante}</p>
                      </div>

                      <div className="mt-2 flex justify-between items-center">
                        <div className="text-xs">
                          <Badge variant="outline" className="mr-1">
                            Ordem: {execution.ordem_execucao || 'N/A'}
                          </Badge>
                          <Badge variant="outline" className="mr-1">
                            {execution.origem}
                          </Badge>
                        </div>
                        
                        {isLinked && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={(e) => {
                              e.stopPropagation();
                              unlinkExecution(execution.id);
                            }}
                          >
                            <Trash className="h-3 w-3 mr-1" /> Desvincular
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}

              {filteredExecutions.length === 0 && (
                <div className="py-8 text-center text-gray-500">
                  <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-20" />
                  <p>Nenhuma execução encontrada com os filtros atuais</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Rodapé de Ação */}
      <div className="mt-6 flex justify-center">
        <Card className="w-full max-w-2xl">
          <CardContent className="pt-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium mb-2">Sessão Selecionada</h3>
                {selectedSession ? (
                  <div className="p-3 bg-gray-50 rounded-md">
                    <p>ID: {selectedSession.id}</p>
                    <p>Data: {formatDate(selectedSession.data_sessao)}</p>
                    <p>Guia: {selectedSession.numero_guia}</p>
                    <p>Ordem: {selectedSession.ordem_execucao}</p>
                  </div>
                ) : (
                  <div className="p-3 bg-gray-50 rounded-md text-gray-400 italic">
                    Nenhuma sessão selecionada
                  </div>
                )}
              </div>
              
              <div>
                <h3 className="text-sm font-medium mb-2">Execução Selecionada</h3>
                {selectedExecution ? (
                  <div className="p-3 bg-gray-50 rounded-md">
                    <p>ID: {selectedExecution.id}</p>
                    <p>Data: {formatDate(selectedExecution.data_execucao)}</p>
                    <p>Guia: {selectedExecution.numero_guia}</p>
                    <p>Paciente: {selectedExecution.paciente_nome}</p>
                  </div>
                ) : (
                  <div className="p-3 bg-gray-50 rounded-md text-gray-400 italic">
                    Nenhuma execução selecionada
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-4 flex justify-center">
              <Button 
                disabled={!selectedSession || !selectedExecution || selectedExecution.sessao_id !== null}
                onClick={handleConfirmLink}
                className="w-48"
              >
                <Link className="mr-2 h-4 w-4" />
                Vincular Itens
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Diálogo de Confirmação */}
      <Dialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Vinculação</DialogTitle>
            <DialogDescription>
              Tem certeza de que deseja vincular a Sessão #{selectedSession?.id} com a Execução #{selectedExecution?.id}?
            </DialogDescription>
          </DialogHeader>
          
          {selectedSession && selectedExecution && (
            <div className="py-4">
              <h3 className="font-medium mb-2">Verificação</h3>
              <div className="grid grid-cols-4 gap-2 text-sm">
                <div className="font-medium">Campo</div>
                <div className="font-medium">Sessão</div>
                <div className="font-medium">Execução</div>
                <div className="font-medium">Correspondência</div>
                
                <div>Guia</div>
                <div>{selectedSession.numero_guia}</div>
                <div>{selectedExecution.numero_guia}</div>
                <div>
                  {selectedSession.numero_guia === selectedExecution.numero_guia ? 
                    <Check className="text-green-500 h-5 w-5" /> : 
                    <X className="text-red-500 h-5 w-5" />}
                </div>
                
                <div>Data</div>
                <div>{formatDate(selectedSession.data_sessao)}</div>
                <div>{formatDate(selectedExecution.data_execucao)}</div>
                <div>
                  {selectedSession.data_sessao === selectedExecution.data_execucao ? 
                    <Check className="text-green-500 h-5 w-5" /> : 
                    <X className="text-red-500 h-5 w-5" />}
                </div>
                
                <div>Ordem</div>
                <div>{selectedSession.ordem_execucao}</div>
                <div>{selectedExecution.ordem_execucao || 'N/A'}</div>
                <div>
                  {selectedSession.ordem_execucao === selectedExecution.ordem_execucao ? 
                    <Check className="text-green-500 h-5 w-5" /> : 
                    <AlertCircle className="text-yellow-500 h-5 w-5" />}
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmDialogOpen(false)}>Cancelar</Button>
            <Button onClick={linkSessionToExecution}>Confirmar Vinculação</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SessionLinkingInterface;