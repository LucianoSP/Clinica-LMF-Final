"use client"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Paciente } from "@/types/paciente"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useEffect, useState } from "react"

interface PacienteSearchProps {
  searchTerm: string
  onSearch: (term: string) => void
  results: Paciente[]
  isLoading: boolean
  onSelect: (paciente: Paciente) => void
}

export function PacienteSearch({
  searchTerm,
  onSearch,
  results,
  isLoading,
  onSelect,
}: PacienteSearchProps) {
  const [localResults, setLocalResults] = useState<Paciente[]>([]);

  useEffect(() => {
    setLocalResults(Array.isArray(results) ? results : []);
  }, [results]);

  const handleSelect = (paciente: Paciente) => {
    onSelect(paciente);
    onSearch('');
  };

  return (
    <div className="space-y-4">
      <Input
        type="search"
        placeholder="Digite pelo menos 3 caracteres para buscar paciente..."
        value={searchTerm}
        onChange={(e) => onSearch(e.target.value)}
      />

      {searchTerm.length > 0 && searchTerm.length < 3 && (
        <p className="text-sm text-muted-foreground mt-2">
          Digite pelo menos 3 caracteres para iniciar a busca
        </p>
      )}

      {searchTerm.length >= 3 && (
        <>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : (
            <div className="space-y-2">
              {localResults.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Nenhum paciente encontrado
                </p>
              ) : (
                localResults.map((paciente) => (
                  <Card
                    key={paciente.id}
                    className="p-4 cursor-pointer hover:bg-accent"
                    onClick={() => handleSelect(paciente)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">{paciente.nome}</p>
                        <p className="text-sm text-muted-foreground">
                          {paciente.cpf}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
} 