"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { formatarData } from "@/lib/utils";
import { UnimedSessao } from "@/app/(auth)/unimed/interfaces";
import { Eye, MoreVertical, RefreshCw, AlertCircle, Check, Clock, Search, Filter, X } from "lucide-react";

interface SessoesTableProps {
  sessoes: UnimedSessao[];
  onReprocessar?: (sessaoId: string) => void;
  onVerDetalhes?: (sessaoId: string) => void;
  isLoading?: boolean;
}

export function SessoesTable({ sessoes, onReprocessar, onVerDetalhes, isLoading = false }: SessoesTableProps) {
  const [filtro, setFiltro] = useState("");
  const [statusFiltro, setStatusFiltro] = useState<string | null>(null);
  const [sessoesFiltradas, setSessoesFiltradas] = useState<UnimedSessao[]>([]);
  const [paginaAtual, setPaginaAtual] = useState(1);
  const itensPorPagina = 10;

  useEffect(() => {
    const filtered = sessoes.filter((sessao) => {
      const matchesFiltro = 
        !filtro || 
        sessao.numero_guia.toLowerCase().includes(filtro.toLowerCase()) ||
        sessao.paciente_nome.toLowerCase().includes(filtro.toLowerCase()) ||
        sessao.paciente_carteirinha.toLowerCase().includes(filtro.toLowerCase());
        
      const matchesStatus = !statusFiltro || sessao.status === statusFiltro;
      
      return matchesFiltro && matchesStatus;
    });
    
    setSessoesFiltradas(filtered);
    setPaginaAtual(1); // Reset para a primeira página quando o filtro mudar
  }, [filtro, statusFiltro, sessoes]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "processado":
        return <Check className="h-4 w-4 text-green-500" />;
      case "erro":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case "pendente":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "processado":
        return "bg-green-100 text-green-800 border-green-200";
      case "erro":
        return "bg-red-100 text-red-800 border-red-200";
      case "pendente":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const limparFiltros = () => {
    setFiltro("");
    setStatusFiltro(null);
  };

  // Paginação
  const totalPaginas = Math.ceil(sessoesFiltradas.length / itensPorPagina);
  const indiceInicial = (paginaAtual - 1) * itensPorPagina;
  const indiceFinal = Math.min(indiceInicial + itensPorPagina, sessoesFiltradas.length);
  const sessoesExibidas = sessoesFiltradas.slice(indiceInicial, indiceFinal);

  const irParaPagina = (pagina: number) => {
    if (pagina >= 1 && pagina <= totalPaginas) {
      setPaginaAtual(pagina);
    }
  };

  const renderPaginacao = () => {
    if (totalPaginas <= 1) return null;

    return (
      <div className="flex items-center justify-between mt-4">
        <div className="text-sm text-muted-foreground">
          Exibindo {indiceInicial + 1}-{indiceFinal} de {sessoesFiltradas.length} sessões
        </div>
        <div className="flex space-x-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => irParaPagina(paginaAtual - 1)}
            disabled={paginaAtual === 1}
          >
            Anterior
          </Button>
          {Array.from({ length: Math.min(5, totalPaginas) }, (_, i) => {
            // Lógica para mostrar páginas ao redor da página atual
            let pageToShow;
            if (totalPaginas <= 5) {
              pageToShow = i + 1;
            } else if (paginaAtual <= 3) {
              pageToShow = i + 1;
            } else if (paginaAtual >= totalPaginas - 2) {
              pageToShow = totalPaginas - 4 + i;
            } else {
              pageToShow = paginaAtual - 2 + i;
            }

            return (
              <Button
                key={i}
                variant={paginaAtual === pageToShow ? "default" : "outline"}
                size="sm"
                onClick={() => irParaPagina(pageToShow)}
                className="w-9"
              >
                {pageToShow}
              </Button>
            );
          })}
          <Button
            variant="outline"
            size="sm"
            onClick={() => irParaPagina(paginaAtual + 1)}
            disabled={paginaAtual === totalPaginas}
          >
            Próxima
          </Button>
        </div>
      </div>
    );
  };

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-2">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-lg">Sessões Capturadas</CardTitle>
            <CardDescription>
              {sessoes.length} sessões no total, {sessoesFiltradas.length} filtradas
            </CardDescription>
          </div>
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por guia, paciente..."
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
                className="pl-9 h-9 md:w-[250px]"
              />
              {filtro && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-9 w-9 p-0"
                  onClick={() => setFiltro("")}
                >
                  <X className="h-4 w-4" />
                  <span className="sr-only">Limpar busca</span>
                </Button>
              )}
            </div>
            <div className="flex space-x-1">
              <Button
                variant={statusFiltro === null ? "default" : "outline"}
                size="sm"
                onClick={() => setStatusFiltro(null)}
                className="h-9"
              >
                Todos
              </Button>
              <Button
                variant={statusFiltro === "processado" ? "default" : "outline"}
                size="sm"
                onClick={() => setStatusFiltro("processado")}
                className="h-9"
              >
                <Check className="h-4 w-4 mr-1" />
                Processados
              </Button>
              <Button
                variant={statusFiltro === "pendente" ? "default" : "outline"}
                size="sm"
                onClick={() => setStatusFiltro("pendente")}
                className="h-9"
              >
                <Clock className="h-4 w-4 mr-1" />
                Pendentes
              </Button>
              <Button
                variant={statusFiltro === "erro" ? "default" : "outline"}
                size="sm"
                onClick={() => setStatusFiltro("erro")}
                className="h-9"
              >
                <AlertCircle className="h-4 w-4 mr-1" />
                Erros
              </Button>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center">
              <RefreshCw className="h-8 w-8 text-blue-500 animate-spin mb-2" />
              <p className="text-muted-foreground">Carregando sessões...</p>
            </div>
          </div>
        ) : sessoesExibidas.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <Filter className="h-12 w-12 text-muted-foreground mb-4 opacity-20" />
            <h3 className="text-lg font-medium mb-1">Nenhuma sessão encontrada</h3>
            <p className="text-muted-foreground mb-4">
              {sessoes.length > 0
                ? "Tente ajustar os filtros para ver mais resultados."
                : "Não há sessões capturadas no momento."}
            </p>
            {(filtro || statusFiltro) && (
              <Button variant="outline" size="sm" onClick={limparFiltros}>
                <X className="h-4 w-4 mr-2" />
                Limpar filtros
              </Button>
            )}
          </div>
        ) : (
          <>
            <div className="rounded-md border overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">Status</TableHead>
                    <TableHead>Guia</TableHead>
                    <TableHead>Paciente</TableHead>
                    <TableHead>Carteirinha</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessoesExibidas.map((sessao) => (
                    <TableRow key={sessao.id} className="group">
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(sessao.status)}
                          <Badge variant="outline" className={cn(getStatusBadge(sessao.status))}>
                            {sessao.status === "processado" ? "Processado" : 
                             sessao.status === "erro" ? "Erro" : 
                             sessao.status === "pendente" ? "Pendente" : sessao.status}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{sessao.numero_guia}</TableCell>
                      <TableCell>{sessao.paciente_nome}</TableCell>
                      <TableCell>{sessao.paciente_carteirinha}</TableCell>
                      <TableCell>{formatarData(new Date(sessao.data_atendimento_completa))}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                          {onVerDetalhes && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => onVerDetalhes(sessao.id)}
                              className="h-8 w-8 p-0"
                            >
                              <Eye className="h-4 w-4" />
                              <span className="sr-only">Ver detalhes</span>
                            </Button>
                          )}
                          {onReprocessar && sessao.status === "erro" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => onReprocessar(sessao.id)}
                              className="h-8 w-8 p-0 text-blue-500 hover:text-blue-600"
                            >
                              <RefreshCw className="h-4 w-4" />
                              <span className="sr-only">Reprocessar</span>
                            </Button>
                          )}
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0"
                              >
                                <MoreVertical className="h-4 w-4" />
                                <span className="sr-only">Abrir menu</span>
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              {onVerDetalhes && (
                                <DropdownMenuItem onClick={() => onVerDetalhes(sessao.id)}>
                                  <Eye className="h-4 w-4 mr-2" />
                                  Ver detalhes
                                </DropdownMenuItem>
                              )}
                              {onReprocessar && sessao.status === "erro" && (
                                <DropdownMenuItem onClick={() => onReprocessar(sessao.id)}>
                                  <RefreshCw className="h-4 w-4 mr-2" />
                                  Reprocessar
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            {renderPaginacao()}
          </>
        )}
      </CardContent>
    </Card>
  );
} 