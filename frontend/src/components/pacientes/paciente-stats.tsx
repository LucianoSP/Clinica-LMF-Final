import { CreditCard, FileText, FolderOpen, Stethoscope, DollarSign } from "lucide-react"

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
}

function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 bg-white hover:border-teal-500 transition-colors">
      <div className="bg-teal-50 p-3 rounded-lg">
        {icon}
      </div>
      <div>
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <div className="mt-1">
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  )
}

interface PacienteStatsProps {
  stats: {
    total_carteirinhas: number;
    total_guias: number;
    total_fichas: number;
    fichas_pendentes: number;
    fichas_conferidas: number;
    fichas_faturadas: number;
    fichas_canceladas: number;
    sessoes_totais: number;
    sessoes_realizadas: number;
    sessoes_pendentes: number;
    valor_faturado: number;
  };
}

const formatarMoeda = (valor: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

export function PacienteStats({ stats }: PacienteStatsProps) {
  const statsData = [
    {
      title: "Carteirinhas",
      value: stats.total_carteirinhas,
      icon: <CreditCard className="h-5 w-5 text-teal-600" />,
    },
    {
      title: "Guias",
      value: stats.total_guias,
      icon: <FileText className="h-5 w-5 text-teal-600" />,
    },
    {
      title: "Fichas",
      value: stats.total_fichas,
      icon: <FolderOpen className="h-5 w-5 text-teal-600" />,
    },
    {
      title: "Sessões Realizadas",
      value: stats.sessoes_realizadas,
      icon: <Stethoscope className="h-5 w-5 text-teal-600" />,
    },
    {
      title: "Valor Faturado",
      value: formatarMoeda(stats.valor_faturado),
      icon: <DollarSign className="h-5 w-5 text-teal-600" />,
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {statsData.map((stat) => (
        <StatCard key={stat.title} title={stat.title} value={stat.value} icon={stat.icon} />
      ))}
    </div>
  )
}