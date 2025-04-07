export function formatDate(dateStr: string) {
  if (!dateStr) return '';
  
  // Se a data já estiver no formato DD/MM/YYYY, retorna ela mesma
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr)) {
    return dateStr;
  }

  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr;
    }
    
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  } catch (error) {
    console.error('Erro ao formatar data:', error);
    return dateStr;
  }
}

export function formatDateToISO(dateStr: string): string {
  if (!dateStr) return '';
  
  try {
    // Se a data estiver no formato DD/MM/YYYY
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr)) {
      const [day, month, year] = dateStr.split('/');
      return `${year}-${month}-${day}`;
    }
    
    // Se a data já for um objeto Date ou uma string ISO
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr;
    }
    
    return date.toISOString().split('T')[0];
  } catch (error) {
    console.error('Erro ao formatar data para ISO:', error);
    return dateStr;
  }
}
