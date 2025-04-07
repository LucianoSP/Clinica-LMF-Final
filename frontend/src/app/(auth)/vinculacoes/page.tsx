"use client"

import { useState, useEffect, useCallback } from "react"
import { Search, Link, Check, Trash2, AlertCircle, Loader2 } from "lucide-react"
import {
  DndContext,
  type DragEndEvent,
  DragOverlay,
  type DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core"
import { restrictToWindowEdges } from "@dnd-kit/modifiers"
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

// Configuração da API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Tipos - Ajustados para refletir modelos do backend (simplificado, pode precisar de mais campos)
// TODO: Importar tipos reais dos schemas do backend se disponíveis
interface Sessao {
  id: string // UUID
  ficha_id?: string | null
  guia_id?: string | null
  numero_guia?: string | null
  data_sessao: string // Date string (YYYY-MM-DD)
  hora_inicio?: string | null
  hora_fim?: string | null
  profissional_id?: string | null
  assinatura_paciente?: string | null
  assinatura_profissional?: string | null
  status?: string | null
  observacoes?: string | null
  codigo_ficha?: string | null
  codigo_ficha_temp?: boolean | null
  ordem_execucao?: number | null
  created_at?: string
  updated_at?: string
  // Campos adicionais que podem ser úteis na UI
  assinada?: boolean // Pode ser derivado do status ou assinatura_paciente/profissional
  numero?: number // Pode ser derivado da ordem_execucao ou outro campo
}

interface Execucao {
  id: string // UUID
  guia_id?: string | null
  sessao_id?: string | null // Chave para verificar vinculação
  data_execucao: string // Date string (YYYY-MM-DD)
  data_atendimento?: string | null // Date string (YYYY-MM-DD)
  paciente_nome?: string | null
  paciente_carteirinha?: string | null
  numero_guia?: string | null
  codigo_ficha?: string | null
  codigo_ficha_temp?: boolean | null
  origem?: string | null
  profissional_executante?: string | null
  conselho_profissional?: string | null
  numero_conselho?: string | null
  uf_conselho?: string | null
  codigo_cbo?: string | null
  status_biometria?: string | null
  observacoes?: string | null
  ordem_execucao?: number | null
  link_manual_necessario?: boolean | null // Novo campo
  created_at?: string
  updated_at?: string
  // Campos adicionais que podem ser úteis na UI
  numero?: string // Pode ser derivado do ID ou outro campo
  procedimento?: string // Pode vir do 'origem' ou outro lugar?
}

// Interface para a resposta paginada da API
interface PaginatedApiResponse<T> {
  success: boolean
  items: T[]
  total: number
  page: number
  total_pages: number
  has_more: boolean
  error?: string | null
  message?: string | null
}

// Componente de Item de Sessão
function SessaoItem({ sessao, isSelected, onSelect, isPotentialMatch }: { 
    sessao: Sessao; 
    isSelected: boolean; 
    onSelect: () => void; 
    isPotentialMatch: boolean; // Novo prop
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: sessao.id,
    data: { type: "sessao", item: sessao },
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : 1,
  }

  // Derivar campos para exibição
  const numeroSessao = sessao.ordem_execucao ?? sessao.numero ?? sessao.id.substring(0, 4)
  const isAssinada = sessao.assinada ?? (!!sessao.assinatura_paciente || !!sessao.assinatura_profissional)
  // @ts-expect-error A assinatura de format com options é válida, erro de linter
  const dataFormatada = sessao.data_sessao ? format(new Date(sessao.data_sessao + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR }) : 'N/A'

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`mb-3 cursor-grab rounded-lg border p-4 transition-all ${ // Simplificado para clareza
        isSelected ? "border-teal-500 bg-teal-50 ring-2 ring-teal-300" 
        : isPotentialMatch ? "border-blue-300 bg-blue-50"
        : "border-slate-200 bg-white"
      } hover:shadow-md`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-slate-900">Sessão: {numeroSessao}</h3>
            {isAssinada && (
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <Check className="mr-1 h-3 w-3" /> Assinada
              </Badge>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">Ficha: {sessao.codigo_ficha ?? 'N/A'}</p>
          <p className="text-sm text-slate-500 mt-1">Ordem: {sessao.ordem_execucao ?? 'N/A'}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-500">{dataFormatada}</p>
          <p className="text-xs text-slate-400">Guia: {sessao.numero_guia ?? 'N/A'}</p>
        </div>
      </div>
      {isPotentialMatch && !isSelected && ( // Mostrar badge apenas se for match, não selecionado, não vinculado e não precisar revisão
         <div className="mt-2 flex justify-end">
           <Badge variant="outline" className="text-blue-600 border-blue-300 bg-blue-100">
             <Link className="mr-1 h-3 w-3" /> Correspondência potencial
           </Badge>
         </div>
      )}
    </motion.div>
  )
}

// Componente de Item de Execução
function ExecucaoItem({
  execucao,
  isSelected,
  onSelect,
  isPotentialMatch // Novo prop
}: { 
    execucao: Execucao; 
    isSelected: boolean; 
    onSelect: () => void; 
    isPotentialMatch: boolean; // Novo prop
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: execucao.id,
    data: { type: "execucao", item: execucao },
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : 1,
  }

  const isVinculada = !!execucao.sessao_id
  const numeroExecucao = execucao.numero ?? execucao.id.substring(0, 4)
  // @ts-expect-error A assinatura de format com options é válida, erro de linter
  const dataFormatada = execucao.data_execucao ? format(new Date(execucao.data_execucao + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR }) : 'N/A'
  const precisaRevisao = execucao.link_manual_necessario === true

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`mb-3 cursor-grab rounded-lg border p-4 transition-all ${ // Simplificado
        isSelected ? "border-teal-500 bg-teal-50 ring-2 ring-teal-300"
        : precisaRevisao ? "border-orange-500 bg-orange-50"
        : isPotentialMatch ? "border-blue-300 bg-blue-50"
        : "border-slate-200 bg-white"
      } hover:shadow-md`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-slate-900">Execução: {numeroExecucao}</h3>
            {isVinculada ? (
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <Check className="mr-1 h-3 w-3" /> Vinculada
              </Badge>
            ) : precisaRevisao ? (
               <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                  <AlertCircle className="mr-1 h-3 w-3" /> Revisão Manual
               </Badge>
            ) : (
              <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
                Não Vinculada
              </Badge>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">Código Ficha: {execucao.codigo_ficha ?? 'N/A'} {execucao.codigo_ficha_temp ? "(Temp)" : ""}</p>
          <div className="mt-2">
            <p className="text-sm text-slate-700">Paciente: {execucao.paciente_nome ?? 'N/A'}</p>
            <p className="text-xs text-slate-500">Profissional: {execucao.profissional_executante ?? 'N/A'}</p>
          </div>
          <p className="text-sm text-slate-500 mt-1">Ordem: {execucao.ordem_execucao ?? 'N/A'}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-500">{dataFormatada}</p>
          <p className="text-xs text-slate-400">Guia: {execucao.numero_guia ?? 'N/A'}</p>
        </div>
      </div>
      {isPotentialMatch && !isSelected && !isVinculada && !precisaRevisao && ( // Mostrar badge apenas se for match, não selecionado, não vinculado e não precisar revisão
         <div className="mt-2 flex justify-end">
           <Badge variant="outline" className="text-blue-600 border-blue-300 bg-blue-100">
             <Link className="mr-1 h-3 w-3" /> Correspondência potencial
           </Badge>
         </div>
      )}
      {execucao.origem && (
        <div className="mt-2 flex justify-end">
          <Badge variant="secondary" className="text-slate-600 bg-slate-100">
            Origem: {execucao.origem}
          </Badge>
        </div>
      )}
    </motion.div>
  )
}

// Componente de Overlay para Drag (sem alterações)
function DragOverlayContent({ type, item }: { type: string; item: any }) {
  // Use os campos corretos dos tipos atualizados
  const displayId = item.ordem_execucao ?? item.id.substring(0, 4)
  const displayName = type === "sessao" ? `Ficha: ${item.codigo_ficha ?? 'N/A'}` : `Paciente: ${item.paciente_nome ?? 'N/A'}`
  return (
    <div className="rounded-lg border border-teal-500 bg-white p-4 shadow-md w-[calc(100%-2rem)] max-w-md">
      {type === "sessao" ? (
        <div>
          <h3 className="font-semibold text-slate-900">Sessão: {displayId}</h3>
          <p className="text-sm text-slate-500">{displayName}</p>
        </div>
      ) : (
        <div>
          <h3 className="font-semibold text-slate-900">Execução: {displayId}</h3>
          <p className="text-sm text-slate-500">{displayName}</p>
        </div>
      )}
    </div>
  )
}

export default function VinculacaoPage() {
  // Estado para dados
  const [sessoes, setSessoes] = useState<Sessao[]>([])
  const [execucoes, setExecucoes] = useState<Execucao[]>([])

  // Estado para carregamento e erros
  const [isLoadingSessoes, setIsLoadingSessoes] = useState(false)
  const [isLoadingExecucoes, setIsLoadingExecucoes] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Estado para filtros
  const [sessaoSearch, setSessaoSearch] = useState("")
  const [execucaoSearch, setExecucaoSearch] = useState("")
  const [filterLinkManual, setFilterLinkManual] = useState<boolean | null>(true)
  const [filterVinculadas, setFilterVinculadas] = useState<string>('nao_vinculada')
  const [dataInicio, setDataInicio] = useState<string>("")
  const [dataFim, setDataFim] = useState<string>("")

  // Estado para seleção e drag-and-drop (mantido)
  const [selectedSessao, setSelectedSessao] = useState<string | null>(null)
  const [selectedExecucao, setSelectedExecucao] = useState<string | null>(null)
  const [activeDragItem, setActiveDragItem] = useState<{ type: string; item: any } | null>(null)

  // Estado para IDs de correspondência potencial
  const [potentialMatchSessaoIds, setPotentialMatchSessaoIds] = useState<Set<string>>(new Set());
  const [potentialMatchExecucaoIds, setPotentialMatchExecucaoIds] = useState<Set<string>>(new Set());

  // Sensores DND (mantido)
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5, // Inicia o drag após mover 5px
      },
    })
  )

  // Função para buscar Sessões
  const fetchSessoes = useCallback(async () => {
    setIsLoadingSessoes(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      params.append('limit', '50')
      if (sessaoSearch) params.append('search', sessaoSearch)
      if (dataInicio) params.append('data_inicio', dataInicio)
      if (dataFim) params.append('data_fim', dataFim)
      // TODO: Adicionar outros filtros de sessão (data, guia, etc.)

      const response = await fetch(`${API_BASE_URL}/api/sessoes?${params.toString()}`)
      if (!response.ok) {
        throw new Error(`Erro ao buscar sessões: ${response.statusText}`)
      }
      const data: PaginatedApiResponse<Sessao> = await response.json()
      if (data.success) {
        setSessoes(data.items)
      } else {
        throw new Error(data.error || "Erro desconhecido ao buscar sessões")
      }
    } catch (err: any) {
      setError(err.message)
      toast.error(`Erro ao buscar sessões: ${err.message}`)
    } finally {
      setIsLoadingSessoes(false)
    }
  }, [sessaoSearch, dataInicio, dataFim])

  // Função para buscar Execuções
  const fetchExecucoes = useCallback(async () => {
    setIsLoadingExecucoes(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      params.append('limit', '50')
      if (execucaoSearch) params.append('search', execucaoSearch)
      if (filterLinkManual !== null) {
        params.append('link_manual_necessario', String(filterLinkManual))
      }
      if (filterVinculadas !== 'todas') {
        params.append('status_vinculacao', filterVinculadas)
      }
      if (dataInicio) params.append('data_inicio', dataInicio)
      if (dataFim) params.append('data_fim', dataFim)
      // TODO: Adicionar filtros de guia, paciente
      params.append('order_column', 'link_manual_necessario')
      params.append('order_direction', 'desc')

      const responseExecucoes = await fetch(`${API_BASE_URL}/api/execucoes?${params.toString()}`)
      if (!responseExecucoes.ok) {
        throw new Error(`Erro ao buscar execuções: ${responseExecucoes.statusText}`)
      }
      const dataExecucoes: PaginatedApiResponse<Execucao> = await responseExecucoes.json()
      if (dataExecucoes.success) {
        setExecucoes(dataExecucoes.items)
      } else {
        throw new Error(dataExecucoes.error || "Erro desconhecido ao buscar execuções")
      }
    } catch (err: any) {
      setError(err.message)
      toast.error(`Erro ao buscar execuções: ${err.message}`)
    } finally {
      setIsLoadingExecucoes(false)
    }
  }, [execucaoSearch, filterLinkManual, filterVinculadas, dataInicio, dataFim])

  // Efeito para buscar dados iniciais ou quando filtros mudam
  useEffect(() => {
    fetchSessoes()
  }, [fetchSessoes])

  useEffect(() => {
    fetchExecucoes()
  }, [fetchExecucoes])

  // Handlers DND (mantidos, mas a lógica de vinculação será movida)
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event
    const itemData = active.data.current
    if (itemData) {
      setActiveDragItem({ type: itemData.type, item: itemData.item })
    }
  }

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveDragItem(null)
    const { active, over } = event

    if (over && active.id !== over.id) {
      const activeType = active.data.current?.type
      const overType = over.data.current?.type

      // Permitir apenas drop de Sessao em Execucao ou vice-versa
      if (activeType && overType && activeType !== overType) {
        if (activeType === "sessao") {
          setSelectedSessao(active.id as string)
          setSelectedExecucao(over.id as string)
        } else {
          setSelectedSessao(over.id as string)
          setSelectedExecucao(active.id as string)
        }
        // A lógica de vincular ocorrerá no botão, não no drop
        toast.info("Sessão e Execução selecionadas para vinculação manual.")
      }
    }
  }

  // Função para calcular correspondências potenciais ao selecionar um item
  const calculatePotentialMatches = (selectedType: "sessao" | "execucao", selectedId: string | null) => {
    setPotentialMatchSessaoIds(new Set()); // Limpa matches anteriores
    setPotentialMatchExecucaoIds(new Set());

    if (!selectedId) return; // Se nada estiver selecionado, não há matches

    if (selectedType === "sessao") {
        const sessao = sessoes.find(s => s.id === selectedId);
        if (!sessao || !sessao.numero_guia) return;

        const matchingExecucoes = new Set<string>();
        execucoes.forEach(exec => {
            if (exec.numero_guia === sessao.numero_guia && !exec.sessao_id) { // Verifica guia e se não está vinculada
                // Poderia adicionar verificação de data próxima aqui também
                matchingExecucoes.add(exec.id);
            }
        });
        setPotentialMatchExecucaoIds(matchingExecucoes);

    } else { // selectedType === "execucao"
        const execucao = execucoes.find(e => e.id === selectedId);
        if (!execucao || !execucao.numero_guia || execucao.sessao_id) return; // Não busca match se já estiver vinculada

        const matchingSessoes = new Set<string>();
        sessoes.forEach(sess => {
             // Verifica se sessão já não está vinculada a outra execução (mais complexo, idealmente checar no backend)
             // Lógica simplificada: apenas verifica a guia
            if (sess.numero_guia === execucao.numero_guia) {
                 // Poderia adicionar verificação de data próxima aqui também
                matchingSessoes.add(sess.id);
            }
        });
         setPotentialMatchSessaoIds(matchingSessoes);
    }
  };

  // Selecionar item ao clicar e calcular matches
  const handleSelect = (type: "sessao" | "execucao", id: string) => {
    let newSelectedId: string | null = null;
    if (type === "sessao") {
      newSelectedId = selectedSessao === id ? null : id;
      setSelectedSessao(newSelectedId);
      setSelectedExecucao(null); // Deseleciona outra coluna
      calculatePotentialMatches("sessao", newSelectedId);
    } else {
      newSelectedId = selectedExecucao === id ? null : id;
      setSelectedExecucao(newSelectedId);
      setSelectedSessao(null); // Deseleciona outra coluna
      calculatePotentialMatches("execucao", newSelectedId);
    }
  }

  // Função Vincular Itens (será implementada a chamada API)
  const vincularItens = async () => {
    if (!selectedSessao || !selectedExecucao) {
      toast.warning("Selecione uma Sessão e uma Execução para vincular.")
      return
    }
    console.log(`Vincular Sessão ${selectedSessao} com Execução ${selectedExecucao}`) // Placeholder
    toast.promise(
      fetch(`${API_BASE_URL}/api/vinculacoes/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ execucao_id: selectedExecucao, sessao_id: selectedSessao }),
      }).then(async (res) => {
        if (!res.ok) {
          const errorData = await res.json().catch(() => ({ detail: res.statusText }))
          throw new Error(errorData.detail || "Erro desconhecido ao vincular")
        }
        return res.json()
      }),
      {
        loading: 'Vinculando itens...', 
        success: (data) => {
          // Refetch data após sucesso
          fetchSessoes()
          fetchExecucoes()
          setSelectedSessao(null)
          setSelectedExecucao(null)
          return data.message || 'Itens vinculados com sucesso!'
        },
        error: (err) => `Erro ao vincular: ${err.message}`,
      }
    )
  }

  // Limpar filtros
  const limparFiltros = () => {
    setSessaoSearch("")
    setExecucaoSearch("")
    setFilterLinkManual(true) // Voltar ao padrão inicial
    setFilterVinculadas('nao_vinculada') // Voltar ao padrão inicial
    setDataInicio("")
    setDataFim("")
    toast.info("Filtros redefinidos para o padrão.")
    // Os useEffects vão disparar o refetch
  }

  // Vincular Automaticamente (será implementada a chamada API)
  const vincularAutomaticamente = async () => {
    console.log("Disparar vinculação automática em lote") // Placeholder
    toast.promise(
      fetch(`${API_BASE_URL}/api/vinculacoes/batch`, { method: 'POST' })
        .then(async (res) => {
          if (!res.ok) {
            const errorData = await res.json().catch(() => ({ detail: res.statusText }))
            throw new Error(errorData.detail || "Erro desconhecido ao iniciar vínculo em lote")
          }
          return res.json()
        }),
      {
        loading: 'Iniciando vinculação automática...', 
        success: (data) => {
          // Refetch data após disparo (pode levar tempo para concluir)
          fetchSessoes()
          fetchExecucoes()
          return data.message || 'Vinculação em lote iniciada!'
        },
        error: (err) => `Erro: ${err.message}`,
      }
    )
  }

  // Lógica de filtro para exibição foi removida, a API faz a filtragem
  // const filteredSessoes = sessoes
  // const filteredExecucoes = execucoes

  return (
    <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd} modifiers={[restrictToWindowEdges]}>
      <div className="container mx-auto p-4 md:p-6">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Vinculação de Sessões e Execuções</CardTitle>
            <CardDescription>Selecione uma sessão e uma execução para vinculá-las manualmente ou dispare a vinculação automática.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col md:flex-row gap-4 flex-wrap">
            <Button onClick={vincularItens} disabled={!selectedSessao || !selectedExecucao}>
              <Link className="mr-2 h-4 w-4" /> Vincular Itens Selecionados
            </Button>
            <Button onClick={vincularAutomaticamente} variant="outline">
              Tentar Vinculação Automática em Lote
            </Button>
            <Button onClick={limparFiltros} variant="secondary">
              Limpar Filtros e Recarregar
            </Button>
          </CardContent>
        </Card>

        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 border border-red-200 rounded-md flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span>Erro ao carregar dados: {error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Coluna de Sessões */}
          <Card>
            <CardHeader>
              <CardTitle>Sessões (Fichas)</CardTitle>
              <div className="flex gap-2 pt-2 flex-wrap">
                <Input
                  placeholder="Buscar sessões..."
                  value={sessaoSearch}
                  onChange={(e) => setSessaoSearch(e.target.value)}
                  className="flex-grow min-w-[150px]"
                />
                <Input
                  type="text"
                  placeholder="Data Início (AAAA-MM-DD)"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  className="w-auto min-w-[160px]"
                />
                <Input
                  type="text"
                  placeholder="Data Fim (AAAA-MM-DD)"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  className="w-auto min-w-[160px]"
                />
              </div>
            </CardHeader>
            <CardContent className="h-[600px] overflow-y-auto bg-slate-50/50 p-4 rounded-b-md relative">
              {isLoadingSessoes && (
                <div className="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
                  <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
                  <span className="ml-2 text-slate-500">Carregando sessões...</span>
                </div>
              )}
              {sessoes.length > 0 ? (
                <SortableContext items={sessoes.map(s => s.id)} strategy={verticalListSortingStrategy}>
                  <AnimatePresence>
                    {sessoes.map(sessao => (
                      <SessaoItem
                        key={sessao.id}
                        sessao={sessao}
                        isSelected={selectedSessao === sessao.id}
                        onSelect={() => handleSelect("sessao", sessao.id)}
                        isPotentialMatch={potentialMatchSessaoIds.has(sessao.id)} // Passar prop
                      />
                    ))}
                  </AnimatePresence>
                </SortableContext>
              ) : !isLoadingSessoes ? (
                <p className="text-center text-slate-500 pt-10">Nenhuma sessão encontrada com os filtros atuais.</p>
              ) : null}
            </CardContent>
          </Card>

          {/* Coluna de Execuções */}
          <Card>
            <CardHeader>
              <CardTitle>Execuções (Unimed / Sistema)</CardTitle>
              <div className="flex gap-2 pt-2 flex-wrap">
                <Input
                  placeholder="Buscar execuções..."
                  value={execucaoSearch}
                  onChange={(e) => setExecucaoSearch(e.target.value)}
                  className="flex-grow min-w-[150px]"
                />
                <Input
                  type="text"
                  placeholder="Data Início (AAAA-MM-DD)"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  className="w-auto min-w-[160px]"
                />
                <Input
                  type="text"
                  placeholder="Data Fim (AAAA-MM-DD)"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  className="w-auto min-w-[160px]"
                />
                <Select
                  value={filterVinculadas}
                  onValueChange={(value) => setFilterVinculadas(value as 'todas' | 'vinculada' | 'nao_vinculada')}
                >
                  <SelectTrigger className="w-auto min-w-[150px]">
                    <SelectValue placeholder="Status Vínculo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todas">Todas</SelectItem>
                    <SelectItem value="vinculada">Vinculadas</SelectItem>
                    <SelectItem value="nao_vinculada">Não Vinculadas</SelectItem>
                  </SelectContent>
                </Select>
                <Select
                  value={filterLinkManual === null ? 'todos' : (filterLinkManual ? 'sim' : 'nao')}
                  onValueChange={(value) => setFilterLinkManual(value === 'todos' ? null : (value === 'sim'))}
                >
                  <SelectTrigger className="w-auto min-w-[150px]">
                    <SelectValue placeholder="Revisão Manual?" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos</SelectItem>
                    <SelectItem value="sim">Sim (Revisão)</SelectItem>
                    <SelectItem value="nao">Não</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent className="h-[600px] overflow-y-auto bg-slate-50/50 p-4 rounded-b-md relative">
              {isLoadingExecucoes && (
                <div className="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
                  <Loader2 className="h-8 w-8 animate-spin text-teal-600" />
                  <span className="ml-2 text-slate-500">Carregando execuções...</span>
                </div>
              )}
              {execucoes.length > 0 ? (
                <SortableContext items={execucoes.map(e => e.id)} strategy={verticalListSortingStrategy}>
                  <AnimatePresence>
                    {execucoes.map(execucao => (
                      <ExecucaoItem
                        key={execucao.id}
                        execucao={execucao}
                        isSelected={selectedExecucao === execucao.id}
                        onSelect={() => handleSelect("execucao", execucao.id)}
                        isPotentialMatch={potentialMatchExecucaoIds.has(execucao.id)} // Passar prop
                      />
                    ))}
                  </AnimatePresence>
                </SortableContext>
              ) : !isLoadingExecucoes ? (
                <p className="text-center text-slate-500 pt-10">Nenhuma execução encontrada com os filtros atuais.</p>
              ) : null}
            </CardContent>
          </Card>
        </div>

        {/* Overlay para o item sendo arrastado */}
        <DragOverlay>
          {activeDragItem ? <DragOverlayContent type={activeDragItem.type} item={activeDragItem.item} /> : null}
        </DragOverlay>
      </div>
    </DndContext>
  )
}

