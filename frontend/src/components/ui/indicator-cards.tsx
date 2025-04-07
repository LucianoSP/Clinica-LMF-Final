"use client"

import { Card, Metric, Text, Flex, ProgressBar } from "@tremor/react"
import { ArrowUpIcon, ArrowDownIcon } from "lucide-react"

const indicators = [
  {
    title: "Sessões",
    total: 1250,
    billed: 1000,
    pending: 250,
    comparison: 5,
  },
  {
    title: "Faturamento",
    total: "R$ 125.000",
    billed: "R$ 100.000",
    pending: "R$ 25.000",
    comparison: -2,
  },
  {
    title: "Divergências",
    total: 50,
    critical: 10,
    avgResolutionTime: "2d 4h",
    topTypes: ["Faturamento", "Documentação", "Autorização"],
  },
  {
    title: "Atendimentos",
    total: 500,
    new: 75,
    returnRate: "85%",
    avgSessions: 5,
  },
]

export function IndicatorCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {indicators.map((indicator) => (
        <Card key={indicator.title} className="max-w-xs mx-auto shadow-md">
          <Text className="text-primary font-medium">{indicator.title}</Text>
          <Metric className="text-primary">{indicator.total}</Metric>
          {indicator.title === "Sessões" && (
            <>
              <Flex className="mt-4">
                <Text>Faturadas</Text>
                <Text className="font-medium">{indicator.billed}</Text>
              </Flex>
              <ProgressBar value={80} className="mt-2" color="blue" />
              <Flex className="mt-2">
                <Text>Pendentes</Text>
                <Text className="font-medium">{indicator.pending}</Text>
              </Flex>
            </>
          )}
          {indicator.title === "Faturamento" && (
            <>
              <Flex className="mt-4">
                <Text>Faturado</Text>
                <Text className="font-medium">{indicator.billed}</Text>
              </Flex>
              <Flex className="mt-2">
                <Text>Pendente</Text>
                <Text className="font-medium">{indicator.pending}</Text>
              </Flex>
            </>
          )}
          {indicator.title === "Divergências" && (
            <>
              <Flex className="mt-4">
                <Text>Críticas</Text>
                <Text className="font-medium text-red-600">{indicator.critical}</Text>
              </Flex>
              <Flex className="mt-2">
                <Text>Tempo médio de resolução</Text>
                <Text className="font-medium">{indicator.avgResolutionTime}</Text>
              </Flex>
            </>
          )}
          {indicator.title === "Atendimentos" && (
            <>
              <Flex className="mt-4">
                <Text>Novos pacientes</Text>
                <Text className="font-medium">{indicator.new}</Text>
              </Flex>
              <Flex className="mt-2">
                <Text>Taxa de retorno</Text>
                <Text className="font-medium">{indicator.returnRate}</Text>
              </Flex>
            </>
          )}
          <Flex className="mt-4">
            <Text>Comparação</Text>
            {indicator.comparison !== undefined ? (
              <Text color={indicator.comparison > 0 ? "emerald" : "red"} className="font-medium">
                {indicator.comparison > 0 ? (
                  <ArrowUpIcon className="inline h-4 w-4 text-emerald-500 mr-1" />
                ) : (
                  <ArrowDownIcon className="inline h-4 w-4 text-red-500 mr-1" />
                )}
                {Math.abs(indicator.comparison)}%
              </Text>
            ) : (
              <Text className="font-medium">N/A</Text>
            )}
          </Flex>
        </Card>
      ))}
    </div>
  )
}

