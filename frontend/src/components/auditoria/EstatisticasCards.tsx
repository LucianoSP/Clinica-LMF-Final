"use client"
import {
  AlertCircle,
  FileSignature,
  Calendar,
  Clock,
  Files,
  FileCheck2,
  AlertTriangle,
  FileWarning,
  FileX,
  Copy,
} from "lucide-react"
import { Card } from "@/components/ui/card"
import { format } from "date-fns"

interface AuditoriaResultado {
  total_protocolos: number
  total_divergencias: number
  total_resolvidas: number
  total_pendentes: number
  total_fichas: number
  total_execucoes: number
  tempo_execucao: string
  divergencias_por_tipo: {
    execucao_sem_ficha?: number
    ficha_sem_execucao?: number
    data_divergente?: number
    sessao_sem_assinatura?: number
    guia_vencida?: number
    quantidade_excedida?: number
    falta_data_execucao?: number
    duplicidade?: number
    [key: string]: number | undefined
  }
  data_execucao: string
}

interface EstatisticasCardsProps {
  resultadoAuditoria: AuditoriaResultado | null
}

const EstatisticasCards = ({ resultadoAuditoria }: EstatisticasCardsProps) => {
  if (!resultadoAuditoria) {
    return (
      <div className="text-center p-4">
        <p className="text-slate-500">Nenhuma auditoria realizada ainda.</p>
      </div>
    )
  }

  const {
    total_divergencias = 0,
    total_resolvidas = 0,
    total_fichas = 0,
    total_execucoes = 0,
    data_execucao,
    tempo_execucao,
    divergencias_por_tipo = {},
  } = resultadoAuditoria

  const {
    execucao_sem_ficha = 0,
    ficha_sem_execucao = 0,
    data_divergente = 0,
    sessao_sem_assinatura = 0,
    guia_vencida = 0,
    quantidade_excedida = 0,
    falta_data_execucao = 0,
    duplicidade = 0,
  } = divergencias_por_tipo

  const mainCards = [
    { title: "Total de Execuções", value: total_execucoes, icon: Files, description: "Execuções analisadas" },
    { title: "Total de Fichas", value: total_fichas, icon: FileCheck2, description: "Fichas verificadas" },
    {
      title: "Divergências",
      value: total_divergencias,
      icon: AlertTriangle,
      description: "Total de divergências encontradas",
      extra: `(${total_divergencias > 0 ? Math.round((total_resolvidas / total_divergencias) * 100) : 0}% resolvidas)`,
    },
    {
      title: "Última Execução",
      value: data_execucao ? format(new Date(data_execucao), "dd/MM/yyyy") : "-",
      icon: Clock,
      description: tempo_execucao ? `Há ${tempo_execucao}` : "",
    },
  ]

  const divergenciasCards = [
    { label: "Sessões sem Assinatura", value: sessao_sem_assinatura, icon: FileSignature },
    { label: "Execuções sem Ficha", value: execucao_sem_ficha, icon: FileWarning },
    { label: "Fichas sem Execução", value: ficha_sem_execucao, icon: FileX },
    { label: "Datas Divergentes", value: data_divergente, icon: Calendar },
    { label: "Guias Vencidas", value: guia_vencida, icon: AlertCircle },
    { label: "Falta Data Execução", value: falta_data_execucao, icon: Clock },
    { label: "Duplicidades", value: duplicidade, icon: Copy },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {mainCards.map((card, index) => (
          <Card
            key={index}
            className="group flex flex-col cursor-pointer rounded-xl border-slate-200 p-6 transition-all hover:border-teal-500 hover:shadow-[0_3px_10px_rgb(0,0,0,0.04)]"
          >
            <div className="flex items-start gap-4">
              <div className="rounded-xl bg-teal-50 p-3">
                <card.icon className="h-6 w-6 text-teal-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 group-hover:text-teal-600 transition-colors">
                  {card.title}
                </h3>
                <p className="text-2xl font-bold text-slate-900 mt-1">{card.value}</p>
                <p className="text-sm text-slate-500 mt-0.5">{card.description}</p>
                {card.extra && <p className="text-sm text-teal-600 mt-1">{card.extra}</p>}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <h3 className="text-lg font-semibold text-slate-900 mb-4">Detalhamento das Divergências</h3>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {divergenciasCards.map((item, index) => (
          <div
            key={index}
            className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 bg-white hover:border-teal-500 transition-colors"
          >
            <div className="bg-teal-50 p-3 rounded-lg">
              <item.icon className="w-5 h-5 text-teal-600" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">{item.label}</h3>
              <div className="mt-1">
                <p className="text-2xl font-semibold text-gray-900">{item.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export { EstatisticasCards }