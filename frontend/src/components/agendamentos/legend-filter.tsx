import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const statusOptions = [
  { id: 'all', label: 'Todos' },
  { id: 'confirmed', label: 'Confirmado' },
  { id: 'missing', label: 'Faltou' },
  { id: 'toConfirm', label: 'A Confirmar' },
  { id: 'reserved', label: 'Reservado' },
  { id: 'substitute', label: 'Substituto' }
]

interface LegendFilterProps {
  onFilterChange: (value: string) => void
}

export function LegendFilter({ onFilterChange }: LegendFilterProps) {
  return (
    <Select onValueChange={onFilterChange} defaultValue="all">
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Filtrar por status" />
      </SelectTrigger>
      <SelectContent>
        {statusOptions.map(option => (
          <SelectItem key={option.id} value={option.id}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

