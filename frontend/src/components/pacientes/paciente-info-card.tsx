import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Calendar, Mail, Phone, User, DollarSign, Users, School, Stethoscope, Activity, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { formatarData, formatarCPF, formatarTelefone } from "@/lib/utils"
import { Paciente } from "@/types/paciente"

interface PacienteInfoCardProps {
  paciente: Paciente;
  onClose: () => void;
}

export function PacienteInfoCard({ paciente, onClose }: PacienteInfoCardProps) {
  return (
    <Card className="w-full transition-all hover:shadow-lg relative">
      <Button
        variant="ghost"
        size="icon"
        onClick={onClose}
        className="absolute right-4 top-4 z-10"
      >
        <X className="h-4 w-4" />
      </Button>
      <CardHeader className="flex flex-row items-center gap-4 space-y-0 pb-6">
        <Avatar className="h-16 w-16 border-2 border-primary/20">
          <AvatarFallback className="bg-teal-50">
            <svg
              className="h-10 w-10 text-teal-600"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="8" r="5" />
              <path d="M9 14h6" />
              <path d="M12 14v7" />
              <path d="M8 19h8" />
              <path d="M7 8c0-1 .5-3 2.5-3" />
              <path d="M16.5 5c2 0 2.5 2 2.5 3" />
              <path d="M10 6.5c0-.5.5-1 1.5-1" />
              <path d="M14 5.5c1 0 1.5.5 1.5 1" />
            </svg>
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <h3 className="text-2xl font-semibold tracking-tight">{paciente.nome}</h3>
            <div className="inline-flex items-center rounded-full border bg-zinc-900 px-3 py-1 text-xs font-medium text-white">
              <Activity className="mr-1 h-4 w-4" />
              Ativo
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Cadastrado em {formatarData(paciente.created_at)}
          </p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">CPF</p>
              <p className="text-sm text-muted-foreground">{formatarCPF(paciente.cpf)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Data de Nascimento</p>
              <p className="text-sm text-muted-foreground">{formatarData(paciente.data_nascimento)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Phone className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Telefone</p>
              <p className="text-sm text-muted-foreground">{formatarTelefone(paciente.telefone)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Email</p>
              <p className="text-sm text-muted-foreground">{paciente.email || '-'}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Valor da Consulta</p>
              <p className="text-sm text-muted-foreground">{paciente.valor_consulta || '-'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Nome do Responsável</p>
              <p className="text-sm text-muted-foreground">{paciente.nome_responsavel || '-'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <School className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Nome da Escola</p>
              <p className="text-sm text-muted-foreground">{paciente.escola_nome || '-'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Stethoscope className="h-4 w-4 text-muted-foreground" />
            <div className="space-y-1">
              <p className="text-sm font-medium leading-none">Patologia</p>
              <p className="text-sm text-muted-foreground">{paciente.patologia_id || '-'}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
} 