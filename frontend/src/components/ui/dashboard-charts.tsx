"use client"

import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, Line, LineChart, XAxis } from "recharts"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const sessionData = [
  { month: "01/02", realizadas: 45, faturadas: 30 },
  { month: "05/02", realizadas: 52, faturadas: 48 },
  { month: "09/02", realizadas: 65, faturadas: 57 },
  { month: "13/02", realizadas: 60, faturadas: 52 },
  { month: "17/02", realizadas: 60, faturadas: 40 },
  { month: "21/02", realizadas: 57, faturadas: 54 },
  { month: "25/02", realizadas: 62, faturadas: 75 },
]

const insuranceData = [
  { convenio: "Convênio A", atendimentos: 1530, faturado: 2000, ticket: 820 },
  { convenio: "Convênio B", atendimentos: 1230, faturado: 1800, ticket: 1010 },
  { convenio: "Convênio C", atendimentos: 1800, faturado: 2600, ticket: 850 },
  { convenio: "Convênio D", atendimentos: 1800, faturado: 2500, ticket: 1000 }
]

const sessionConfig = {
  realizadas: {
    label: "Sessões Realizadas",
    color: "hsl(var(--chart-1))",
  },
  faturadas: {
    label: "Sessões Faturadas",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig

const insuranceConfig = {
  atendimentos: {
    label: "Volume de Atendimentos",
    color: "hsl(var(--chart-1))",
  },
  faturado: {
    label: "Valor Faturado",
    color: "hsl(var(--chart-2))",
  },
  ticket: {
    label: "Ticket Médio",
    color: "hsl(var(--chart-3))",
  },
} satisfies ChartConfig

export function DashboardCharts() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Evolução de Sessões</CardTitle>
          <CardDescription>Fevereiro 2024</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={sessionConfig}>
            <LineChart
              accessibilityLayer
              data={sessionData}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="month"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
              <Line
                dataKey="realizadas"
                type="monotone"
                stroke="var(--color-realizadas)"
                strokeWidth={2}
                dot={false}
              />
              <Line
                dataKey="faturadas"
                type="monotone"
                stroke="var(--color-faturadas)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
        <CardFooter>
          <div className="flex w-full items-start gap-2 text-sm">
            <div className="grid gap-2">
              <div className="flex items-center gap-2 font-medium leading-none">
                Crescimento de 5.2% este mês <TrendingUp className="h-4 w-4" />
              </div>
              <div className="flex items-center gap-2 leading-none text-muted-foreground">
                Mostrando evolução das sessões nos últimos 30 dias
              </div>
            </div>
          </div>
        </CardFooter>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comparativo por Convênio</CardTitle>
          <CardDescription>Fevereiro 2024</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={insuranceConfig}>
            <BarChart
              accessibilityLayer
              data={insuranceData}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="convenio"
                tickLine={false}
                tickMargin={10}
                axisLine={false}
              />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent indicator="dashed" />}
              />
              <Bar dataKey="atendimentos" fill="var(--color-atendimentos)" radius={4} />
              <Bar dataKey="faturado" fill="var(--color-faturado)" radius={4} />
              <Bar dataKey="ticket" fill="var(--color-ticket)" radius={4} />
            </BarChart>
          </ChartContainer>
        </CardContent>
        <CardFooter>
          <div className="flex flex-col gap-2 text-sm">
            <div className="flex gap-2 font-medium leading-none">
              Crescimento de 5.2% este mês <TrendingUp className="h-4 w-4" />
            </div>
            <div className="leading-none text-muted-foreground">
              Comparativo de performance entre convênios
            </div>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
