import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, isValid } from "date-fns"
import { parseISO } from 'date-fns/parseISO';
import { ptBR } from "date-fns/locale"
import { formatInTimeZone } from 'date-fns-tz'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Função principal para formatar datas
export function formatarData(data: string | Date | undefined | null, incluirHora: boolean = false): string {
  if (!data) return '-';
  try {
    const date = typeof data === 'string' ? parseISO(data) : data;
    return formatInTimeZone(
      date, 
      'America/Sao_Paulo', 
      incluirHora ? 'dd/MM/yyyy HH:mm' : 'dd/MM/yyyy', 
      { locale: ptBR }
    );
  } catch (error) {
    console.error('Erro ao formatar data:', error);
    return '-';
  }
}

// Função para converter data para formato ISO
export function formatDateToISO(dateStr: string): string {
  try {
    const [day, month, year] = dateStr.split('/');
    const date = new Date(Number(year), Number(month) - 1, Number(day));
    
    if (!isValid(date)) return dateStr;
    return format(date, 'yyyy-MM-dd');
  } catch {
    return dateStr;
  }
}

// Formatação de moeda
export function formatCurrency(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return 'R$ 0,00';
  
  const numericValue = typeof value === 'string' ? parseFloat(value) : value;
  
  // Se o valor não for um número válido após a conversão
  if (isNaN(numericValue)) return 'R$ 0,00';
  
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(numericValue);
}

// Formatação de CPF
export function formatarCPF(cpf: string | null | undefined): string {
  if (!cpf) return '-';
  const cleaned = cpf.replace(/\D/g, '');
  if (cleaned.length !== 11) return cpf;
  return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

// Formatação de telefone
export function formatarTelefone(telefone: string | null | undefined): string {
  if (!telefone) return '-';
  const cleaned = telefone.replace(/\D/g, '');
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  }
  return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
}

// Formatação de tamanho de arquivo
export function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`;
}


export const formatDateTime = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  try {
    let parsedDate: Date;
    
    if (typeof date === 'string') {
      parsedDate = parseISO(date);
      if (!isValid(parsedDate)) {
        const [dateStr, timeStr] = date.split(' ');
        const [day, month, year] = dateStr.split('/');
        const [hours, minutes, seconds] = (timeStr || '00:00:00').split(':');
        
        parsedDate = new Date(
          Number(year),
          Number(month) - 1,
          Number(day),
          Number(hours || 0),
          Number(minutes || 0),
          Number(seconds || 0)
        );
      }
    } else {
      parsedDate = date;
    }
    
    if (!isValid(parsedDate)) return 'Data inválida';
    return format(parsedDate, 'dd/MM/yyyy HH:mm');
  } catch {
    return 'Data inválida';
  }
};


export const formatCPF = (cpf: string | null | undefined): string => {
  if (!cpf) return '-';
  const cleaned = cpf.replace(/\D/g, '');
  if (cleaned.length !== 11) return cpf;
  return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

export const formatPhone = (phone: string | null | undefined): string => {
  if (!phone) return '-';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  }
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  }
  return phone;
};


export function formatarDataHora(data: string | Date | null): string {
    if (!data) return '';
    
    const date = typeof data === 'string' ? new Date(data) : data;
    
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}


//------------ Teste de calendario ------------





