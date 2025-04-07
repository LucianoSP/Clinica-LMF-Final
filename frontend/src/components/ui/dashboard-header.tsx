"use client"

import { CalendarIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function DashboardHeader() {
  return (
    <div className="flex flex-col sm:flex-row justify-between items-center mb-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-4 sm:mb-0">Dashboard Gerencial</h1>
      <div className="flex flex-col sm:flex-row items-center gap-4">
        <p className="text-sm text-slate-600">16 de fevereiro de 2025</p>
        <Select defaultValue="today">
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Selecione o período" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Hoje</SelectItem>
            <SelectItem value="week">Última Semana</SelectItem>
            <SelectItem value="month">Último Mês</SelectItem>
            <SelectItem value="custom">Personalizado</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" className="w-[280px] justify-start text-left font-normal">
          <CalendarIcon className="mr-2 h-4 w-4" />
          16 de fevereiro - 16 de fevereiro
        </Button>
      </div>
    </div>
  )
}

