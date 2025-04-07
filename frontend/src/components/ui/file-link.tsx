import { FileText } from 'lucide-react';
import { Button } from './button';

interface FileLinkProps {
  url?: string;
  label?: string;
}

export function FileLink({ url, label = "Ver arquivo" }: FileLinkProps) {
  if (!url) return <span className="text-muted-foreground text-sm">Sem arquivo</span>;

  return (
    <Button
      variant="ghost"
      size="sm"
      className="text-blue-600 hover:text-blue-800"
      onClick={() => window.open(url, '_blank')}
    >
      <FileText className="h-4 w-4 mr-1" />
      {label}
    </Button>
  );
} 