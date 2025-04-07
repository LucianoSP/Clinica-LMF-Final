import { cn } from '@/lib/utils'

const statusItems = [
  { id: 'confirmed', label: 'Confirmado', color: 'bg-green-500' },
  { id: 'missing', label: 'Faltou', color: 'bg-yellow-500' },
  { id: 'toConfirm', label: 'A Confirmar', color: 'bg-blue-500' },
  { id: 'reserved', label: 'Reservado', color: 'bg-purple-500' },
  { id: 'substitute', label: 'Substituto', color: 'bg-cyan-500' }
]

export function Legend() {
  return (
    <div className="flex items-center gap-4">
      {statusItems.map(item => (
        <div key={item.id} className="flex items-center gap-1.5">
          <div className={cn('h-3 w-3 rounded-full', item.color)} />
          <span className="text-xs text-muted-foreground">{item.label}</span>
        </div>
      ))}
    </div>
  )
}

