"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ChevronLeft, FileDown, Database, Loader2, RefreshCw, AlertCircle, CheckCircle, ChevronDown } from "lucide-react";
import { SortableTable } from "@/components/ui/SortableTable";
import { useDebounce } from "@/hooks/useDebounce";
import { toast } from "sonner";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import importacaoService, { ControleImportacaoItem } from "@/services/importacaoService";
import api from '@/services/api';
import { LoadingSpinner } from '@/components/ui/loading';
import { PaginatedResponse } from '@/types/api';
import { Badge } from "@/components/ui/badge";

type TabelaAba = Record<string, any>;

interface PassoResultado {
  success: boolean;
  message: string;
  novos_registros?: number;
  registros_atualizados?: number;
  registros_existentes?: number;
  erros_mapeamento?: number;
  total_processado?: number;
  registros_nao_encontrados?: number;
}

interface ImportacaoGeralResultado {
  success: boolean;
  message: string;
  resultados?: Record<string, PassoResultado>;
}

interface TableState {
  data: TabelaAba[];
  loading: boolean;
  currentPage: number;
  totalPages: number;
  totalItems: number;
}

type TableKey = 
  | "profissoes"
  | "especialidades"
  | "locais"
  | "salas"
  | "usuarios"
  | "tipos_pagamento"
  | "usuarios_profissoes"
  | "usuarios_especialidades"
  | "agendamentos_profissionais";

const initialTableState: TableState = {
  data: [],
  loading: false,
  currentPage: 1,
  totalPages: 1,
  totalItems: 0,
};

const endpointMap: Record<TableKey, string> = {
  profissoes: '/api/tabelas-aba/profissoes',
  especialidades: '/api/tabelas-aba/especialidades',
  locais: '/api/tabelas-aba/locais',
  salas: '/api/tabelas-aba/salas',
  usuarios: '/api/tabelas-aba/usuarios',
  tipos_pagamento: '/api/tabelas-aba/tipos-pagamento',
  usuarios_profissoes: '/api/tabelas-aba/usuarios-profissoes',
  usuarios_especialidades: '/api/tabelas-aba/usuarios-especialidades',
  agendamentos_profissionais: '/api/tabelas-aba/agendamentos-profissionais',
};

export default function TabelasAbaPage() {
  const [tablesState, setTablesState] = useState<Record<TableKey, TableState>>({
    profissoes: { ...initialTableState },
    especialidades: { ...initialTableState },
    locais: { ...initialTableState },
    salas: { ...initialTableState },
    usuarios: { ...initialTableState },
    tipos_pagamento: { ...initialTableState },
    usuarios_profissoes: { ...initialTableState },
    usuarios_especialidades: { ...initialTableState },
    agendamentos_profissionais: { ...initialTableState },
  });

  const [activeTab, setActiveTab] = useState<TableKey>("profissoes");
  const [bancoDados, setBancoDados] = useState("abalarissa_db");
  const [importando, setImportando] = useState(false);
  const [relacionando, setRelacionando] = useState(false);
  const [pageSize, setPageSize] = useState(10);
  const [accordionValue, setAccordionValue] = useState<string[]>(["item-1"]);

  // Estados específicos para controle de loading dos botões individuais
  const [loadingState, setLoadingState] = useState<Record<string, boolean>>({
    profissoes: false,
    especialidades: false,
    locais: false,
    salas: false,
    usuarios_aba: false,
    tipos_pagamento: false,
    codigos_faturamento: false,
    usuarios_profissoes: false,
    usuarios_especialidades: false,
    relacionar: false,
    corrigir: false,
    importar_tudo: false
  });

  const [controleImportacao, setControleImportacao] = useState<ControleImportacaoItem[]>([]);
  const [loadingControle, setLoadingControle] = useState<boolean>(true);

  const fetchData = useCallback(async (tabKey: TableKey, page: number) => {
    const endpoint = endpointMap[tabKey];
    if (!endpoint) return;

    setTablesState(prev => ({
      ...prev,
      [tabKey]: { ...prev[tabKey], loading: true },
    }));

    try {
      const offset = (page - 1) * pageSize;
      const params = new URLSearchParams({
        limit: String(pageSize),
        offset: String(offset),
      });

      const response = await api.get<PaginatedResponse<TabelaAba>>(`${endpoint}?${params}`);
      
      setTablesState(prev => ({
        ...prev,
        [tabKey]: {
          ...prev[tabKey],
          data: response.data.items || [],
          currentPage: response.data.page || 1,
          totalPages: response.data.total ? Math.ceil(response.data.total / pageSize) : 1,
          totalItems: response.data.total || 0,
          loading: false,
        },
      }));

    } catch (error) {
      console.error(`Erro ao buscar dados de ${endpoint}:`, error);
      toast.error(`Falha ao carregar dados de ${tabKey}`);
      setTablesState(prev => ({
        ...prev,
        [tabKey]: {
          ...prev[tabKey],
          data: [],
          currentPage: 1,
          totalPages: 1,
          totalItems: 0,
          loading: false,
        },
      }));
    } 
  }, [pageSize]);

  useEffect(() => {
    const currentState = tablesState[activeTab];
    if (currentState) {
       fetchData(activeTab, currentState.currentPage);
    }
    // Busca os dados de controle
    const fetchControle = async () => {
      setLoadingControle(true);
      try {
        const result = await importacaoService.getControleImportacao();
        if (result.success) {
          setControleImportacao(result.data);
        }
      } catch (error: any) {
        console.error("Erro ao buscar controle de importação:", error);
        toast.error(`Erro ao buscar status das importações: ${error.message || 'Erro desconhecido'}`);
      } finally {
        setLoadingControle(false);
      }
    };
    fetchControle();
  }, [activeTab, fetchData]);

  const handlePageChange = (tabKey: TableKey, pageIndex: number) => {
    const newPage = pageIndex + 1;
    const { totalPages } = tablesState[tabKey];
    if (newPage >= 1 && newPage <= totalPages && newPage !== tablesState[tabKey].currentPage) {
        setTablesState(prev => ({
            ...prev,
            [tabKey]: { ...prev[tabKey], currentPage: newPage },
        }));
    }
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setTablesState(prev => ({
      ...prev,
      [activeTab]: { ...prev[activeTab], currentPage: 1 },
    }));
  };

  // Função para formatar data de forma legível
  const formatarDataControle = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleString('pt-BR');
    } catch {
      return isoString; // Retorna a string original se houver erro
    }
  }
  
  // Função para obter a data relativa (há quanto tempo)
  const getRelativeTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        if (diffHours === 0) {
          const diffMinutes = Math.floor(diffMs / (1000 * 60));
          return `${diffMinutes} min atrás`;
        }
        return `${diffHours}h atrás`;
      } else if (diffDays === 1) {
        return `Ontem`;
      } else if (diffDays < 30) {
        return `${diffDays} dias atrás`;
      } else {
        return formatarDataControle(isoString).split(" ")[0];
      }
    } catch {
      return "Data desconhecida";
    }
  }

  // Atualiza o controle após uma importação bem-sucedida
  const atualizarControleAposImportacao = async () => {
    try {
        const result = await importacaoService.getControleImportacao();
        if (result.success) {
          setControleImportacao(result.data);
        }
      } catch (error: any) {
        console.error("Erro ao atualizar controle de importação:", error);
        // Não mostrar toast aqui para não poluir
      } 
  };

  // Função genérica para lidar com o clique dos botões de importação individual
  const handleImportClick = async (tabela: string, importFunction: (db: string) => Promise<any>) => {
    setLoadingState(prev => ({ ...prev, [tabela]: true }));
    try {
      const result = await importFunction(bancoDados);
      const msgSucesso = result.message || `Importação de ${tabela.replace(/_/g, ' ')} concluída!`
      if (result.success) {
        toast.success(msgSucesso);
        atualizarControleAposImportacao(); // Atualiza controle
        if (Object.keys(endpointMap).includes(tabela)) {
           await fetchData(tabela as TableKey, 1); 
        }
      } else {
          toast.error(result.message || `Erro ao importar ${tabela}.`);
      }
      console.log(`Resultado importação ${tabela}:`, result);
      
    } catch (error: any) {
      console.error(`Erro ao importar ${tabela}:`, error);
      toast.error(`Erro ao importar ${tabela}: ${error.message || 'Erro desconhecido'}`);
    } finally {
      setLoadingState(prev => ({ ...prev, [tabela]: false }));
    }
  };

  // Funções para relacionar e corrigir (adaptadas para usar o novo estado de loading)
  const relacionarAgendamentos = async () => {
    setLoadingState(prev => ({ ...prev, relacionar: true }));
    try {
      const result = await importacaoService.relacionarAgendamentos();
      toast.success(`Relacionamento concluído! Salas: ${result.salas_relacionadas}, Locais: ${result.locais_relacionados}, Especialidades: ${result.especialidades_relacionadas}. Total Verificado: ${result.total_agendamentos_verificados}`);
    } catch (error: any) {
      console.error("Erro ao relacionar agendamentos:", error);
      toast.error(`Erro ao relacionar agendamentos: ${error.message || 'Erro desconhecido'}`);
    } finally {
      setLoadingState(prev => ({ ...prev, relacionar: false }));
    }
  };

  const corrigirMapeamentos = async () => {
    setLoadingState(prev => ({ ...prev, corrigir: true }));
    try {
      const result = await importacaoService.corrigirAgendamentosImportados();
      toast.info(`Correção de mapeamentos: ${result.message}`);
    } catch (error: any) {
      console.error("Erro ao corrigir mapeamentos:", error);
      toast.error(`Erro ao corrigir mapeamentos: ${error.message || 'Erro desconhecido'}`);
    } finally {
      setLoadingState(prev => ({ ...prev, corrigir: false }));
    }
  };

  // Função para Importar Tudo (reativada)
  const handleImportarTudo = async () => {
    setLoadingState(prev => ({ ...prev, importar_tudo: true }));
    toast.info(`Iniciando importação completa do banco: ${bancoDados}`, { id: 'import-start' });
    try {
      const result = await importacaoService.importarTudoSistemaAba(bancoDados);
      if (result.success && result.resultados) {
        toast.success("Importação geral concluída com sucesso! Verifique os detalhes.");
        console.log("Detalhes da importação geral:", result.resultados);
        atualizarControleAposImportacao(); // Atualiza controle
        fetchData(activeTab, 1); 
      } else {
        toast.error(result.message || "Falha na importação geral.", { id: 'import-error'});
      }
    } catch (error: any) {
      console.error("Erro ao importar tudo:", error);
      toast.error(`Erro na importação geral: ${error.message || 'Erro desconhecido'}`, { id: 'import-error' });
    } finally {
       setLoadingState(prev => ({ ...prev, importar_tudo: false }));
    }
  };

  const generateColumns = (data: TabelaAba[]) => {
      if (!data || data.length === 0) return [];
      const allKeys = new Set<string>();
      data.forEach(row => Object.keys(row).forEach(key => allKeys.add(key)));
      return Array.from(allKeys).map(key => ({
          key: key,
          label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          sortable: true,
          render: (value: any) => {
            if (typeof value === 'boolean') return value ? 'Sim' : 'Não';
            if (typeof value === 'object' && value !== null) return JSON.stringify(value);
            if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
              try { return new Date(value).toLocaleString('pt-BR'); } catch { /* ignore */ }
            }
            return value;
          }
      }));
  };

  const renderTable = (tabKey: TableKey) => {
    const { data, loading, currentPage, totalPages, totalItems } = tablesState[tabKey];
    const columns = generateColumns(data);

    const pageCount = Math.max(totalPages, 1);

    return (
      <Card>
        <CardHeader>
          <CardTitle className="capitalize">{tabKey.replace(/_/g, ' ')}</CardTitle>
        </CardHeader>
        <CardContent>
          <SortableTable<TabelaAba>
            data={data || []}
            columns={columns}
            loading={loading}
            sortable
            pageSize={pageSize}
            pageCount={pageCount}
            pageIndex={currentPage - 1}
            totalRecords={totalItems}
            onPageChange={(pageIndex) => handlePageChange(tabKey, pageIndex)}
            onPageSizeChange={handlePageSizeChange}
            onSort={() => {}}
          />
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container py-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Tabelas Sistema ABA</h1>
          <p className="text-slate-500 mt-1">Importar, visualizar e gerenciar tabelas auxiliares do sistema ABA.</p>
        </div>
        <Link
          href="/cadastros"
          className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Voltar
        </Link>
      </div>

      {/* Accordion para agrupar as seções de importação */}
      <Accordion 
        type="multiple" 
        value={accordionValue}
        onValueChange={setAccordionValue}
        className="w-full"
      >
        {/* Seção: Status das Importações */}
        <AccordionItem value="item-1" className="border rounded-lg px-4 mb-4 shadow-sm bg-white">
          <AccordionTrigger className="hover:no-underline py-4">
            <div className="flex items-center">
              <Database className="h-5 w-5 mr-2 text-teal-600" />
              <span className="font-semibold text-lg">Status das Importações</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="pt-2 pb-4">
              {loadingControle ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner />
                </div>
              ) : controleImportacao.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {controleImportacao.map((item) => (
                    <div key={item.nome_tabela} className="bg-slate-50 p-3 rounded-md border border-slate-200">
                      <div className="font-medium capitalize text-slate-800">
                        {item.nome_tabela.replace(/_/g, ' ')}
                      </div>
                      <div className="flex justify-between items-center mt-1">
                        <Badge variant="outline" className="text-xs bg-white">
                          {getRelativeTime(item.ultima_importacao)}
                        </Badge>
                        <span className="text-xs text-slate-500">
                          {formatarDataControle(item.ultima_importacao)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-slate-500">
                  <p>Nenhum registro de controle encontrado.</p>
                </div>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Seção: Ações de Importação */}
        <AccordionItem value="item-2" className="border rounded-lg px-4 mb-4 shadow-sm bg-white">
          <AccordionTrigger className="hover:no-underline py-4">
            <div className="flex items-center">
              <FileDown className="h-5 w-5 mr-2 text-indigo-600" />
              <span className="font-semibold text-lg">Importação Individual de Tabelas</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 pt-2 pb-4">
              <Button 
                onClick={() => handleImportClick('profissoes', importacaoService.importarProfissoes)} 
                disabled={loadingState.profissoes}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.profissoes ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Profissões
              </Button>
              <Button 
                onClick={() => handleImportClick('especialidades', importacaoService.importarEspecialidades)} 
                disabled={loadingState.especialidades}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.especialidades ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Especialidades
              </Button>
              <Button 
                onClick={() => handleImportClick('locais', importacaoService.importarLocais)} 
                disabled={loadingState.locais}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.locais ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Locais
              </Button>
              <Button 
                onClick={() => handleImportClick('salas', importacaoService.importarSalas)} 
                disabled={loadingState.salas}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.salas ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Salas
              </Button>
              <Button 
                onClick={() => handleImportClick('usuarios_aba', importacaoService.importarUsuariosAba)} 
                disabled={loadingState.usuarios_aba}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.usuarios_aba ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Usuários ABA
              </Button>
              <Button 
                onClick={() => handleImportClick('tipos_pagamento', importacaoService.importarTiposPagamento)} 
                disabled={loadingState.tipos_pagamento}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.tipos_pagamento ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Tipos Pagamento
              </Button>
              <Button 
                onClick={() => handleImportClick('codigos_faturamento', importacaoService.importarCodigosFaturamento)} 
                disabled={loadingState.codigos_faturamento}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.codigos_faturamento ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Proc./Cod.Fat.
              </Button>
              <Button 
                onClick={() => handleImportClick('usuarios_profissoes', importacaoService.importarUsuariosProfissoes)} 
                disabled={loadingState.usuarios_profissoes}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.usuarios_profissoes ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Usuários/Profissões
              </Button>
              <Button 
                onClick={() => handleImportClick('usuarios_especialidades', importacaoService.importarUsuariosEspecialidades)} 
                disabled={loadingState.usuarios_especialidades}
                variant="outline"
                className="h-12 bg-white hover:bg-teal-50 hover:text-teal-600 hover:border-teal-300 transition-colors"
                size="sm"
              >
                {loadingState.usuarios_especialidades ? <LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> : null}
                Usuários/Espec.
              </Button>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Seção: Ações Gerais */}
        <AccordionItem value="item-3" className="border rounded-lg px-4 mb-4 shadow-sm bg-white">
          <AccordionTrigger className="hover:no-underline py-4">
            <div className="flex items-center">
              <RefreshCw className="h-5 w-5 mr-2 text-amber-600" />
              <span className="font-semibold text-lg">Ações Gerais</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 pb-6">
              <div className="bg-gradient-to-br from-teal-50 to-white p-4 rounded-lg border border-teal-100 shadow-sm hover:shadow-md transition-all duration-200"> 
                <Button 
                  onClick={handleImportarTudo} 
                  disabled={Object.values(loadingState).some(Boolean)}
                  variant="default"
                  className="w-full mb-2 bg-teal-600 hover:bg-teal-700"
                >
                  {loadingState.importar_tudo ? (
                    <><LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> Importando...</>
                  ) : (
                    <><Database className="mr-2 h-4 w-4" /> Importar Todas Tabelas</>
                  )}
                </Button>
                <p className="text-xs text-slate-600 text-center">
                  Importa/Atualiza todas tabelas auxiliares de uma vez
                </p>
              </div>

              <div className="bg-gradient-to-br from-indigo-50 to-white p-4 rounded-lg border border-indigo-100 shadow-sm hover:shadow-md transition-all duration-200">
                <Button 
                  onClick={relacionarAgendamentos} 
                  disabled={Object.values(loadingState).some(Boolean)}
                  variant="default"
                  className="w-full mb-2 bg-indigo-600 hover:bg-indigo-700"
                >
                  {loadingState.relacionar ? (
                    <><LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> Relacionando...</>
                  ) : (
                    <><RefreshCw className="mr-2 h-4 w-4" /> Relacionar Agendamentos</>
                  )}
                </Button>
                <p className="text-xs text-slate-600 text-center">
                  Vincula agendamentos às tabelas importadas
                </p>
              </div>

              <div className="bg-gradient-to-br from-amber-50 to-white p-4 rounded-lg border border-amber-100 shadow-sm hover:shadow-md transition-all duration-200">
                <Button 
                  onClick={corrigirMapeamentos} 
                  disabled={Object.values(loadingState).some(Boolean)} 
                  variant="default"
                  className="w-full mb-2 bg-amber-600 hover:bg-amber-700"
                >
                  {loadingState.corrigir ? (
                    <><LoadingSpinner className="mr-2 h-4 w-4 animate-spin" /> Corrigindo...</>
                  ) : (
                    <><AlertCircle className="mr-2 h-4 w-4" /> Corrigir Mapeamentos</>
                  )}
                </Button>
                <p className="text-xs text-slate-600 text-center">
                  Tenta vincular agendamentos importados sem paciente
                </p>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      {/* Visualização de Tabelas */}
      <Card className="shadow-md border-slate-200">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-white border-b pb-6">
          <CardTitle className="text-xl text-slate-800">Visualizar Tabelas Importadas</CardTitle>
          <CardDescription>Visualize os dados que foram importados para o sistema atual.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as TableKey)} className="w-full">
            <div className="bg-slate-50 border-b">
              <TabsList className="w-full h-auto flex-wrap py-1">
                {(Object.keys(endpointMap) as TableKey[]).map(key => (
                  <TabsTrigger 
                    key={key} 
                    value={key}
                    className="py-2 px-4 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-sm m-1"
                  >
                    {key.replace(/_/g, ' ')}
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>
            {(Object.keys(endpointMap) as TableKey[]).map(key => (
              <TabsContent key={key} value={key} className="m-0 p-6">
                {renderTable(key)}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}