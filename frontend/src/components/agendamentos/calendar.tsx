import { cn } from '@/lib/utils'
import { format, addHours, setHours, setMinutes } from 'date-fns'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Appointment } from './appointment'

// Definição local do tipo para AppointmentType
type AppointmentStatus = 'confirmed' | 'missing' | 'toConfirm' | 'reserved' | 'substitute'
interface AppointmentType {
  id: string
  room: string
  startTime: Date
  endTime: Date
  patientName: string
  therapistName: string
  therapyType: string
  status: AppointmentStatus
}

// Generate rooms
const rooms = Array.from({ length: 8 }, (_, i) => ({
  id: `C${String(i + 1).padStart(2, '0')}`,
  name: `C ${i + 1}`
}))

// Dados para gerar agendamentos aleatórios
const patientNames = [
  'Maria Silva', 'João Santos', 'Ana Oliveira', 'Pedro Costa', 'Carla Ferreira',
  'Ricardo Almeida', 'Sofia Rodrigues', 'Miguel Pereira', 'Beatriz Gomes', 'Luís Martins'
]

const therapistNames = [
  'Dr. Silva', 'Dra. Santos', 'Dr. Oliveira', 'Dra. Costa', 'Dr. Ferreira',
  'Dra. Almeida', 'Dr. Rodrigues', 'Dra. Pereira', 'Dr. Gomes', 'Dra. Martins'
]

const therapyTypes = ['Fonoaudiologia', 'ABA', 'Terapia Ocupacional', 'Fisioterapia', 'Psicologia']

const statuses: AppointmentStatus[] = ['confirmed', 'missing', 'toConfirm', 'reserved', 'substitute']

// Função auxiliar para obter um item aleatório de um array
function getRandomItem<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)]
}

// Gerar agendamentos aleatórios
function generateMockAppointments(date: Date): AppointmentType[] {
  const appointments: AppointmentType[] = []
  const startHour = 7
  const endHour = 19

  for (let hour = startHour; hour < endHour; hour++) {
    for (let room = 1; room <= rooms.length; room++) {
      if (Math.random() < 0.3) { // 30% de chance de ter um agendamento neste horário
        const startTime = setHours(setMinutes(new Date(date), 0), hour)
        const endTime = addHours(startTime, 1)
        const roomId = `C${String(room).padStart(2, '0')}`

        appointments.push({
          id: `${roomId}-${startTime.getTime()}`,
          room: roomId,
          startTime,
          endTime,
          patientName: getRandomItem(patientNames),
          therapistName: getRandomItem(therapistNames),
          therapyType: getRandomItem(therapyTypes),
          status: getRandomItem(statuses)
        })
      }
    }
  }

  return appointments
}

// Criar agendamentos de exemplo
const today = new Date()
const mockAppointments = generateMockAppointments(today)

interface CalendarProps {
  filter: string
}

export function Calendar({ filter }: CalendarProps) {
  // Generate time slots from 7:00 to 19:00
  const timeSlots = Array.from({ length: 13 }, (_, i) => 
    addHours(setHours(setMinutes(new Date(), 0), 7), i)
  )

  const filteredAppointments = filter === 'all'
    ? mockAppointments
    : mockAppointments.filter(apt => apt.status === filter)

  return (
    <div className="flex-1 rounded-lg border">
      <ScrollArea className="h-[calc(100vh-13rem)]">
        <div className="relative">
          {/* Header */}
          <div className="sticky top-0 z-20 flex bg-background">
            <div className="w-20 flex-none border-b border-r">
              <div className="h-12" />
            </div>
            <div className="flex">
              {rooms.map((room) => (
                <div
                  key={room.id}
                  className="flex w-[150px] flex-none items-center justify-center border-b border-r py-3 text-sm font-medium"
                >
                  {room.name}
                </div>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="flex">
            {/* Time column */}
            <div className="w-20 flex-none">
              {timeSlots.map((time) => (
                <div
                  key={time.toISOString()}
                  className="flex h-24 items-center justify-end border-b border-r px-4 text-sm text-muted-foreground"
                >
                  {format(time, 'HH:mm')}
                </div>
              ))}
            </div>

            {/* Appointment grid */}
            <div className="flex">
              {rooms.map((room) => (
                <div key={room.id} className="w-[150px] flex-none">
                  {timeSlots.map((time) => {
                    const appointment = filteredAppointments?.find(
                      (apt) =>
                        apt.room === room.id &&
                        apt.startTime.getHours() === time.getHours()
                    )

                    return (
                      <div
                        key={time.toISOString()}
                        className={cn(
                          'relative h-24 border-b border-r',
                          appointment && 'bg-muted/50'
                        )}
                      >
                        {appointment && (
                          <Appointment
                            appointment={appointment}
                            className="absolute inset-1"
                          />
                        )}
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  )
}

