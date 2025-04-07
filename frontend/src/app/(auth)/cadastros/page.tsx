'use client'

import { FileText, Users, CreditCard, FileCheck, Stethoscope, ClipboardCheck, GitCompare, Database } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import Link from 'next/link'

const modules = [
  { icon: FileText, title: "Planos de Saúde", desc: "Gestão de planos de saúde", href: '/cadastros/planos_saude' },
  { icon: Users, title: "Pacientes", desc: "Gestão de pacientes", href: '/cadastros/pacientes' },
  { icon: CreditCard, title: "Carteirinhas", desc: "Gestão de carteirinhas", href: '/cadastros/carteirinhas' },
  { icon: FileCheck, title: "Guias", desc: "Gestão de guias médicas", href: '/cadastros/guias' },
  { icon: Stethoscope, title: "Procedimentos", desc: "Registro médico", href: '/cadastros/procedimentos' },
  { icon: ClipboardCheck, title: "Fichas de Presença", desc: "Controle", href: '/cadastros/fichas' },
  { icon: Database, title: "Tabelas Sistema Aba", desc: "Importação das tabelas", href: '/cadastros/tabelas_aba' },
]

export default function CadastrosPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Cadastros</h1>
        <p className="text-slate-500">Gerencie os cadastros do sistema</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modules.map((module) => (
          <Link key={module.href} href={module.href}>
            <Card
              className="group relative overflow-hidden border-slate-200 transition-all hover:shadow-lg hover:border-teal-500/50"
            >
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-teal-50 text-teal-600 ring-1 ring-teal-100">
                    <module.icon className="h-6 w-6" />
                  </div>

                  <div className="space-y-1">
                    <h2 className="text-xl font-medium text-slate-900 group-hover:text-teal-600">{module.title}</h2>
                    <p className="text-slate-500">{module.desc}</p>
                  </div>
                </div>

                {/* Decorative corner gradient */}
                <div className="absolute right-0 top-0 -z-10 h-24 w-24 rounded-bl-[100px] bg-gradient-to-br from-teal-50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}