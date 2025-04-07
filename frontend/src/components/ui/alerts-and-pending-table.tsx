"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"

const criticalDivergences = [
  { id: 1, status: "Aberto", type: "Faturamento", timeOpen: "2d 4h" },
  { id: 2, status: "Em Análise", type: "Documentação", timeOpen: "1d 6h" },
  // Adicione mais dados...
]

const pendingSessions = [
  { id: 1, insurance: "Convênio A", patient: "João Silva", value: "R$ 150,00" },
  { id: 2, insurance: "Convênio B", patient: "Maria Santos", value: "R$ 180,00" },
  // Adicione mais dados...
]

export function AlertsAndPendingTable() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="bg-white p-4 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4 text-primary">Divergências Críticas</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="font-semibold">Status</TableHead>
              <TableHead className="font-semibold">Tipo</TableHead>
              <TableHead className="font-semibold">Tempo em Aberto</TableHead>
              <TableHead className="font-semibold">Ação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {criticalDivergences.map((divergence) => (
              <TableRow key={divergence.id}>
                <TableCell>{divergence.status}</TableCell>
                <TableCell>{divergence.type}</TableCell>
                <TableCell>{divergence.timeOpen}</TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">
                    Resolver
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="bg-white p-4 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4 text-primary">Sessões Pendentes de Faturamento</h2>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="font-semibold">Convênio</TableHead>
              <TableHead className="font-semibold">Paciente</TableHead>
              <TableHead className="font-semibold">Valor</TableHead>
              <TableHead className="font-semibold">Ação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {pendingSessions.map((session) => (
              <TableRow key={session.id}>
                <TableCell>{session.insurance}</TableCell>
                <TableCell>{session.patient}</TableCell>
                <TableCell>{session.value}</TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">
                    Faturar
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

