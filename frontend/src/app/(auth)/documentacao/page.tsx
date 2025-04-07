'use client';

import { useState, useEffect } from 'react';
import { documentacaoService } from '@/services/documentacaoService';
import { MarkdownViewer } from '@/components/ui/markdown-viewer';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import mermaid from 'mermaid';

export default function DocumentacaoPage() {
  const [arquivos, setArquivos] = useState<string[]>([]);
  const [conteudoAtual, setConteudoAtual] = useState<string>('');
  const [arquivoAtual, setArquivoAtual] = useState<string>('indice_geral.md');
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [filtro, setFiltro] = useState('');

  // Carregar a lista de arquivos disponíveis
  useEffect(() => {
    const carregarArquivos = async () => {
      try {
        const response = await documentacaoService.listarArquivos();
        if (response.success && response.items) {
          setArquivos(response.items);
        } else {
          setErro(response.message || 'Erro ao carregar lista de arquivos');
        }
      } catch (error) {
        setErro('Erro ao conectar com o servidor');
        console.error('Erro:', error);
      }
    };

    carregarArquivos();
  }, []);

  // Carregar o conteúdo do arquivo atual
  useEffect(() => {
    const carregarConteudo = async () => {
      setCarregando(true);
      setErro(null);
      
      try {
        const response = await documentacaoService.obterArquivo(arquivoAtual);
        if (response.success && response.data) {
          setConteudoAtual(response.data);
        } else {
          setErro(response.message || 'Erro ao carregar arquivo');
        }
      } catch (error) {
        setErro('Erro ao carregar conteúdo do arquivo');
        console.error('Erro:', error);
      } finally {
        setCarregando(false);
      }
    };

    if (arquivoAtual) {
      carregarConteudo();
    }
  }, [arquivoAtual]);

  // Função para carregar um arquivo quando clicado
  const handleArquivoClick = (nomeArquivo: string) => {
    setArquivoAtual(nomeArquivo);
    // Rolar para o topo quando mudar de arquivo
    window.scrollTo(0, 0);
  };

  // Função para processar links dentro do markdown
  useEffect(() => {
    const handleMarkdownLinks = () => {
      const links = document.querySelectorAll('.prose a');
      links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href.endsWith('.md')) {
          link.addEventListener('click', (e) => {
            e.preventDefault();
            // Extrair apenas o nome do arquivo do caminho completo
            const parts = href.split('/');
            const fileName = parts[parts.length - 1];
            handleArquivoClick(fileName);
          });
        }
      });
    };

    if (!carregando) {
      // Pequeno timeout para garantir que o markdown foi renderizado
      setTimeout(handleMarkdownLinks, 100);
    }
  }, [conteudoAtual, carregando]);

  // Filtrar a lista de arquivos
  const arquivosFiltrados = filtro 
    ? arquivos.filter(arquivo => 
        arquivo.toLowerCase().includes(filtro.toLowerCase()))
    : arquivos;

  // Inicializar Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    });
  }, []);

  // Processar diagramas Mermaid após o markdown ser renderizado
  useEffect(() => {
    const processarDiagramasMermaid = async () => {
      if (!carregando) {
        try {
          // Pequeno delay para garantir que o markdown foi renderizado
          await new Promise(resolve => setTimeout(resolve, 100));
          
          // Procurar por blocos de código mermaid
          const elementos = document.querySelectorAll('code.language-mermaid');
          
          elementos.forEach(async (elemento) => {
            try {
              const htmlElemento = elemento as HTMLElement;
              const preElement = htmlElemento.parentElement;
              
              if (preElement && !preElement.classList.contains('mermaid-processado')) {
                preElement.classList.add('mermaid-processado');
                preElement.classList.add('mermaid');
                preElement.innerHTML = htmlElemento.textContent || '';
                
                await mermaid.run({
                  nodes: [preElement],
                });
              }
            } catch (error) {
              console.error('Erro ao processar diagrama Mermaid:', error);
            }
          });
        } catch (error) {
          console.error('Erro ao processar diagramas:', error);
        }
      }
    };

    processarDiagramasMermaid();
  }, [conteudoAtual, carregando]);

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-4rem)] overflow-hidden bg-background">
      {/* Barra lateral com lista de arquivos */}
      <div className="w-full lg:w-80 border-r border-border bg-muted/30 flex flex-col">
        <div className="p-4 border-b">
          <h3 className="font-semibold mb-2">Documentação</h3>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Buscar documentos..."
              className="pl-8"
              value={filtro}
              onChange={(e) => setFiltro(e.target.value)}
            />
          </div>
        </div>
        
        <ScrollArea className="flex-grow">
          <div className="p-2">
            {arquivosFiltrados.map((arquivo) => (
              <Button
                key={arquivo}
                variant={arquivo === arquivoAtual ? "secondary" : "ghost"}
                className={`w-full justify-start text-left px-2 py-1.5 mb-1 ${
                  arquivo === arquivoAtual ? 'bg-secondary font-medium' : ''
                }`}
                onClick={() => handleArquivoClick(arquivo)}
              >
                {arquivo.replace('.md', '')}
              </Button>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Área principal com conteúdo */}
      <div className="flex-grow overflow-y-auto">
        <ScrollArea className="h-full">
          <div className="max-w-4xl mx-auto p-6 pb-24">
            {carregando ? (
              // Esqueleto de carregamento
              <div>
                <Skeleton className="h-12 w-3/4 mb-6" />
                <Skeleton className="h-6 w-full mb-4" />
                <Skeleton className="h-6 w-full mb-4" />
                <Skeleton className="h-6 w-3/4 mb-8" />
                <Skeleton className="h-10 w-1/2 mb-4" />
                <Skeleton className="h-6 w-full mb-4" />
                <Skeleton className="h-6 w-full mb-4" />
                <Skeleton className="h-6 w-5/6 mb-4" />
              </div>
            ) : erro ? (
              // Exibição de erro
              <div className="p-4 border border-red-300 bg-red-50 rounded-md text-red-800">
                <h3 className="font-bold mb-2">Erro ao carregar documento</h3>
                <p>{erro}</p>
              </div>
            ) : (
              // Conteúdo do markdown
              <MarkdownViewer content={conteudoAtual} />
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
} 