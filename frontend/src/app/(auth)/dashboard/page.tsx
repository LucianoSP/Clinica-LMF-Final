import { Card } from "@/components/ui/card"
import { DashboardHeader } from "@/components/ui/dashboard-header"
import { DashboardCharts } from "@/components/ui/dashboard-charts"
import { ArrowUpIcon, ArrowDownIcon, Activity, DollarSign, AlertCircle, Users } from "lucide-react"

interface MetricDetail {
  label: string;
  value: string;
  highlight?: boolean;
}

interface Metric {
  title: string;
  value: string;
  icon: React.ElementType;
  details: MetricDetail[];
  comparison: {
    value: number | string;
    trend: "up" | "down";
  };
}

const metrics: Metric[] = [
  {
    title: "Sessões",
    value: "1250",
    icon: Activity,
    details: [
      { label: "Faturadas", value: "1000" },
      { label: "Pendentes", value: "250" },
    ],
    comparison: { value: 5, trend: "up" },
  },
  {
    title: "Faturamento",
    value: "R$ 125.000",
    icon: DollarSign,
    details: [
      { label: "Faturado", value: "R$ 100.000" },
      { label: "Pendente", value: "R$ 25.000" },
    ],
    comparison: { value: 2, trend: "down" },
  },
  {
    title: "Divergências",
    value: "50",
    icon: AlertCircle,
    details: [
      { label: "Críticas", value: "10", highlight: true },
      { label: "Tempo médio de resolução", value: "2d 4h" },
    ],
    comparison: { value: "NaN", trend: "down" },
  },
  {
    title: "Atendimentos",
    value: "500",
    icon: Users,
    details: [
      { label: "Novos pacientes", value: "75" },
      { label: "Taxa de retorno", value: "85%" },
    ],
    comparison: { value: "NaN", trend: "down" },
  },
]

export default function DashboardPage() {
  return (
    <div className="p-6">
      <DashboardHeader />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <Card
              key={metric.title}
              className="group flex flex-col cursor-pointer rounded-xl border-slate-200 p-6 transition-all hover:border-teal-500 hover:shadow-[0_3px_10px_rgb(0,0,0,0.04)]"
            >
              <div className="flex items-start gap-4">
                <div className="rounded-xl bg-teal-50 p-3">
                  <Icon className="h-6 w-6 text-teal-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-900 group-hover:text-teal-600 transition-colors">
                    {metric.title}
                  </h3>
                  <p className="text-2xl font-bold text-slate-900 mt-1">{metric.value}</p>
                </div>
              </div>
              <div className="space-y-2 mt-4">
                {metric.details.map((detail) => (
                  <div key={detail.label} className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">{detail.label}</span>
                    <span className={`text-sm font-medium ${detail.highlight ? "text-red-500" : "text-slate-900"}`}>
                      {detail.value}
                    </span>
                  </div>
                ))}
                <div className="flex justify-between items-center pt-2">
                  <span className="text-sm text-slate-600">Comparação</span>
                  <span
                    className={`text-sm font-medium flex items-center gap-1 ${
                      metric.comparison.trend === "up" ? "text-teal-500" : "text-red-500"
                    }`}
                  >
                    {metric.comparison.trend === "up" ? (
                      <ArrowUpIcon className="h-4 w-4" />
                    ) : (
                      <ArrowDownIcon className="h-4 w-4" />
                    )}
                    {metric.comparison.value}%
                  </span>
                </div>
              </div>
            </Card>
          )
        })}
      </div>
      <DashboardCharts />
    </div>
  )
}

