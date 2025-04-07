"use client"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Paciente } from "@/types/paciente"
import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface PacienteSearchProps {
  searchTerm: string
  onSearch: (term: string) => void
  results: Paciente[]
  isLoading: boolean
  onSelect: (paciente: Paciente) => void
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export function PacienteSearch({
  searchTerm,
  onSearch,
  results,
  isLoading,
  onSelect,
  currentPage,
  totalPages,
  onPageChange,
}: PacienteSearchProps) {
  const handleSelect = (paciente: Paciente) => {
    onSelect(paciente);
    onSearch(''); // Limpa o termo de busca
  };

  return (
    <div className="space-y-4">
      <Input
        type="search"
        placeholder="Buscar paciente..."
        value={searchTerm}
        onChange={(e) => onSearch(e.target.value)}
      />

      {searchTerm.length >= 3 && ( // Só mostra resultados se tiver 3+ caracteres
        <>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : (
            <div className="space-y-2">
              {results.map((paciente) => (
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
              ))}
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              <Button
                variant="outline"
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Próxima
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
} 