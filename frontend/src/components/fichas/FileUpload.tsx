import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';
import { Upload, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import api from '@/services/api';
import { formatDateToISO } from '@/utils/date';
import { format } from 'date-fns';

interface FileInfo {
  nome: string;
  url: string;
}

interface UploadedFile {
  nome: string;
  url: string;
}

interface UploadResponse {
  success?: boolean;
  message?: string;
  results?: Array<{
    filename: string;
    status: 'success' | 'error';
    message?: string;
    data_atendimento?: string;
    id?: string;
    uploaded_files?: Array<{ nome: string; url: string }>;
  }>;
  resultados?: Array<{
    filename: string;
    status: 'success' | 'error';
    message?: string;
    storage_id?: string;
    pendente_id?: string;
    url?: string;
  }>;
}

interface PromptInfo {
  path: string;
  title: string;
  description: string;
}

interface FileUploadProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess?: () => void;
}

const generateFileName = (file: File, result: any): string => {
  const extension = file.name.split('.').pop();
  const codigoFicha = result.codigo_ficha || 'sem-codigo';
  const nomePaciente = (result.paciente_nome || 'sem-nome')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, '-');
  const dataAtual = format(new Date(), 'yyyyMMdd');
  
  return `${codigoFicha}_${nomePaciente}_${dataAtual}.${extension}`;
};

export function FileUpload({ isOpen, onClose, onUploadSuccess }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [modeloIA, setModeloIA] = useState<string>('claude');
  const [promptPath, setPromptPath] = useState<string>('padrao');
  const [promptsDisponiveis, setPromptsDisponiveis] = useState<PromptInfo[]>([]);
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(false);
  const [promptInputMode, setPromptInputMode] = useState<'select' | 'manual'>('select');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  // Carregar prompts disponíveis quando o modal abrir
  useEffect(() => {
    if (isOpen) {
      carregarPromptsDisponiveis();
    }
  }, [isOpen]);

  const carregarPromptsDisponiveis = async () => {
    setIsLoadingPrompts(true);
    try {
      const response = await api.get<{
        success: boolean;
        prompts: PromptInfo[];
        message?: string;
      }>('/api/prompts-disponiveis');
      
      if (response.data.success) {
        setPromptsDisponiveis(response.data.prompts);
      } else {
        console.error('Erro ao carregar prompts:', response.data.message);
      }
    } catch (error) {
      console.error('Erro ao carregar prompts:', error);
    } finally {
      setIsLoadingPrompts(false);
    }
  };

  const handleUpload = async (e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();

    if (files.length === 0) {
      toast.error('Selecione pelo menos um arquivo para upload');
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      
      // Adiciona o modelo de IA selecionado ao FormData
      formData.append('modelo_ia', modeloIA);
      
      // Adiciona o caminho do prompt personalizado, se fornecido
      if (promptPath.trim() && promptPath !== "padrao") {
        formData.append('prompt_path', promptPath.trim());
      }

      // Usa o endpoint unificado que verifica automaticamente se a guia existe
      // e salva no local apropriado (fichas ou fichas_pendentes)
      const endpoint = '/api/upload-pdf';
      const response = await api.post<UploadResponse>(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const results = response.data;
      
      // Verifica se a resposta tem a estrutura esperada
      if (results.success) {
        toast.success('Arquivos processados com sucesso!', {
          duration: 5000
        });
        onUploadSuccess?.();
        onClose();
      } else if (results.resultados) {
        // Nova estrutura de resposta com 'resultados'
        const successResults = results.resultados.filter(r => r.status === 'success');
        const errorResults = results.resultados.filter(r => r.status === 'error');

        // Mostra erros primeiro
        if (errorResults.length > 0) {
          errorResults.forEach(result => {
            toast.error(`Erro no arquivo ${result.filename}`, {
              description: result.message,
              duration: 8000
            });
          });
        }

        // Se tiver sucessos, mostra depois
        if (successResults.length > 0) {
          toast.success(`${successResults.length} ${successResults.length === 1 ? 'arquivo processado' : 'arquivos processados'} com sucesso!`, {
            duration: 5000
          });
          onUploadSuccess?.();
        }

        // Fecha o modal depois de mostrar as mensagens
        setTimeout(() => {
          onClose();
        }, 500);
      } else if (results.results) {
        // Estrutura antiga com 'results'
        const successResults = results.results.filter(r => r.status === 'success');
        const errorResults = results.results.filter(r => r.status === 'error');

        // Mostra erros primeiro
        if (errorResults.length > 0) {
          errorResults.forEach(result => {
            toast.error(`Erro no arquivo ${result.filename}`, {
              description: result.message,
              duration: 8000
            });
          });
        }

        // Se tiver sucessos, mostra depois
        if (successResults.length > 0) {
          toast.success(`${successResults.length} ${successResults.length === 1 ? 'arquivo processado' : 'arquivos processados'} com sucesso!`, {
            duration: 5000
          });
          onUploadSuccess?.();
        }

        // Fecha o modal depois de mostrar as mensagens
        setTimeout(() => {
          onClose();
        }, 500);
      } else {
        // Resposta não reconhecida
        toast.error('Formato de resposta não reconhecido', {
          description: 'Contate o suporte técnico',
          duration: 8000
        });
        console.error('Formato de resposta não reconhecido:', results);
      }
    } catch (err) {
      console.error('Erro no upload:', err);
      toast.error('Erro ao fazer upload dos arquivos', {
        description: err instanceof Error ? err.message : 'Erro desconhecido',
        duration: 8000
      });
      
      // Fecha o modal depois de mostrar o erro
      setTimeout(() => {
        onClose();
      }, 500);
    } finally {
      setFiles([]);
      setIsLoading(false);
    }
  };

  // Limpa os arquivos quando o modal é fechado
  useEffect(() => {
    if (!isOpen) {
      setFiles([]);
      setIsLoading(false); // Garante que o loading seja resetado
      setPromptPath('padrao');
      setPromptInputMode('select');
    }
  }, [isOpen]);

  // Função para limpar estado ao fechar
  const handleClose = useCallback(() => {
    setFiles([]);
    setIsLoading(false);
    setPromptPath('padrao');
    setPromptInputMode('select');
    onClose();
  }, [onClose]);

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Upload de Arquivos PDF</DialogTitle>
        </DialogHeader>

        {/* Explicação do modo de upload unificado */}
        <div className="text-xs text-center mt-1">
          <span className="text-blue-700">
            O sistema verificará automaticamente se a guia existe e processará adequadamente.
          </span>
        </div>
        
        {/* Seleção de modelo de IA */}
        <div className="mt-4">
          <Label htmlFor="modelo-ia">Modelo de IA para processamento</Label>
          <Select value={modeloIA} onValueChange={setModeloIA}>
            <SelectTrigger id="modelo-ia" className="w-full">
              <SelectValue placeholder="Selecione o modelo de IA" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="claude">Claude (Anthropic)</SelectItem>
              <SelectItem value="gemini">Gemini (Google)</SelectItem>
              <SelectItem value="mistral">Mistral</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-gray-500 mt-1">
            Escolha o modelo de IA para processar e extrair informações dos arquivos PDF.
          </p>
        </div>
        
        {/* Campo para prompt personalizado */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <Label htmlFor="prompt-path">Prompt Personalizado (opcional)</Label>
            <div className="flex items-center space-x-2">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => {
                  setPromptInputMode('select');
                  setPromptPath('padrao');
                }}
                className={promptInputMode === 'select' ? 'bg-gray-100' : ''}
              >
                Selecionar
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => {
                  setPromptInputMode('manual');
                  setPromptPath('');
                }}
                className={promptInputMode === 'manual' ? 'bg-gray-100' : ''}
              >
                Manual
              </Button>
            </div>
          </div>
          
          {promptInputMode === 'select' ? (
            <>
              <Select value={promptPath} onValueChange={setPromptPath}>
                <SelectTrigger id="prompt-select" className="w-full">
                  <SelectValue placeholder="Selecione um prompt personalizado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="padrao">Prompt Padrão</SelectItem>
                  {promptsDisponiveis.map((prompt) => (
                    <SelectItem key={prompt.path} value={prompt.path}>
                      {prompt.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {promptPath && promptPath !== "padrao" && promptsDisponiveis.find(p => p.path === promptPath)?.description && (
                <p className="text-xs text-gray-600 mt-1">
                  {promptsDisponiveis.find(p => p.path === promptPath)?.description}
                </p>
              )}
            </>
          ) : (
            <Input
              id="prompt-path"
              placeholder="Ex: prompts/unimed/padrao.md"
              value={promptPath}
              onChange={(e) => setPromptPath(e.target.value)}
            />
          )}
          <p className="text-xs text-gray-500 mt-1">
            {promptInputMode === 'select' 
              ? 'Selecione um prompt personalizado ou escolha "Prompt Padrão" para usar o prompt padrão do sistema.' 
              : 'Informe o caminho para um arquivo de prompt personalizado. Deixe em branco para usar o prompt padrão.'}
          </p>
        </div>

        <div className="mt-4">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-teal-500 bg-teal-50' : 'border-gray-300 hover:border-teal-500'}`}
          >
            <input {...getInputProps()} />
            <p className="text-gray-600">
              Arraste e solte arquivos PDF aqui, ou clique para selecionar
            </p>
          </div>

          {files.length > 0 && (
            <div className="mt-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-medium text-gray-700">Arquivos Selecionados</h3>
              </div>
              <div className="space-y-2">
                {files.map((file) => (
                  <div key={file.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-700">{file.name}</div>
                      <div className="text-xs text-gray-500">
                        {(file.size / 1024).toFixed(2)} KB
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleUpload}
              disabled={isLoading || files.length === 0}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processando...
                </>
              ) : (
                'Processar'
              )}
            </Button>
          </div>

          {isLoading && (
            <div className="mt-4">
              <div className="h-1 w-full bg-gray-200 rounded">
                <div className="h-1 bg-teal-600 rounded animate-pulse"></div>
              </div>
              <p className="text-sm text-gray-500 mt-2 text-center">
                Processando arquivos, por favor aguarde...
              </p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
} 