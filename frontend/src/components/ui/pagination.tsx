"use client"

import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
import { ButtonProps, Button } from "@/components/ui/button"

interface PaginationProps {
  pageCount: number
  pageIndex: number
  pageSize: number
  totalRecords: number
  onPageChange: (page: number) => void
  onPageSizeChange?: (size: number) => void
  className?: string
}

interface PaginationButtonProps extends ButtonProps {
  isActive?: boolean
}

function PaginationButton({
  className,
  isActive,
  ...props
}: PaginationButtonProps) {
  return (
    <Button
      variant={isActive ? "outline" : "ghost"}
      size="icon"
      className={cn(
        "h-8 w-8",
        isActive && "bg-muted hover:bg-muted",
        className
      )}
      {...props}
    />
  )
}

export function Pagination({
  pageCount,
  pageIndex,
  pageSize,
  totalRecords,
  onPageChange,
  onPageSizeChange,
  className,
}: PaginationProps) {
  // Gera array de números de página
  const generatePages = () => {
    const pages: (number | string)[] = []
    const maxVisible = 7 // Número máximo de botões visíveis
    const halfVisible = Math.floor(maxVisible / 2)

    if (pageCount <= maxVisible) {
      // Se houver poucas páginas, mostra todas
      for (let i = 0; i < pageCount; i++) {
        pages.push(i)
      }
    } else {
      // Sempre mostra a primeira página
      pages.push(0)

      // Decide onde começar e terminar
      let start = Math.max(pageIndex - halfVisible, 1)
      let end = Math.min(pageIndex + halfVisible, pageCount - 2)

      // Ajusta para manter o número de botões consistente
      if (start <= 1) {
        end = Math.min(maxVisible - 2, pageCount - 2)
      }
      if (end >= pageCount - 2) {
        start = Math.max(pageCount - maxVisible + 1, 1)
      }

      // Adiciona ellipsis no início se necessário
      if (start > 1) {
        pages.push("...")
      }

      // Adiciona as páginas do meio
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      // Adiciona ellipsis no final se necessário
      if (end < pageCount - 2) {
        pages.push("...")
      }

      // Sempre mostra a última página
      pages.push(pageCount - 1)
    }

    return pages
  }

  const pages = generatePages()

  return (
    <div className={cn("flex items-center justify-between px-2", className)}>
      <div className="flex items-center space-x-6 lg:space-x-8">
        <div className="flex w-[100px] items-center justify-center text-sm font-medium">
          {`${pageIndex * pageSize + 1}-${Math.min((pageIndex + 1) * pageSize, totalRecords)} de ${totalRecords}`}
        </div>
        <div className="flex items-center space-x-2">
          <PaginationButton
            aria-label="Ir para primeira página"
            onClick={() => onPageChange(0)}
            disabled={pageIndex === 0}
          >
            <ChevronLeft className="h-4 w-4" />
            <ChevronLeft className="h-4 w-4 -ml-2" />
          </PaginationButton>
          <PaginationButton
            aria-label="Ir para página anterior"
            onClick={() => onPageChange(pageIndex - 1)}
            disabled={pageIndex === 0}
          >
            <ChevronLeft className="h-4 w-4" />
          </PaginationButton>
          {pages.map((page, i) => (
            page === "..." ? (
              <PaginationButton
                key={`ellipsis-${i}`}
                disabled
              >
                <MoreHorizontal className="h-4 w-4" />
              </PaginationButton>
            ) : (
              <PaginationButton
                key={page}
                onClick={() => onPageChange(page as number)}
                isActive={pageIndex === page}
                aria-label={`Ir para página ${(page as number) + 1}`}
              >
                {(page as number) + 1}
              </PaginationButton>
            )
          ))}
          <PaginationButton
            aria-label="Ir para próxima página"
            onClick={() => onPageChange(pageIndex + 1)}
            disabled={pageIndex >= pageCount - 1}
          >
            <ChevronRight className="h-4 w-4" />
          </PaginationButton>
          <PaginationButton
            aria-label="Ir para última página"
            onClick={() => onPageChange(pageCount - 1)}
            disabled={pageIndex >= pageCount - 1}
          >
            <ChevronRight className="h-4 w-4" />
            <ChevronRight className="h-4 w-4 -ml-2" />
          </PaginationButton>
        </div>
      </div>
    </div>
  )
}
