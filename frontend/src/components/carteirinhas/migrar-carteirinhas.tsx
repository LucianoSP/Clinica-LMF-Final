"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Database, ChevronDown, ChevronUp } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { carteirinhaService } from "@/services/carteirinhaService";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface MigracaoResultado {
  success: boolean;
  message: string;
  details?: any[];
  errors?: ErroItem[];
}

interface ErroItem {
  paciente_id: string;
  nome_paciente: string;
  numero_carteirinha: string;
  erro: string;
}

export function MigrarCarteirinhas() {
  const [isLoading, setIsLoading] = useState(false);
  const [tamanhoBatch, setTamanhoBatch] = useState(100);
  const [resultado, setResultado] = useState<MigracaoResultado | null>(null);

  const { toast } = useToast();

  const handleMigrar = async () => {
    setIsLoading(true);
    setResultado(null);

    try {
      const response = await carteirinhaService.migrarDePacientes(tamanhoBatch);

      setResultado(response);

      toast({
        title: response.success ? "Migração concluída" : "Erro na migração",
        description: response.message,
        variant: response.success ? "default" : "destructive",
      });
    } catch (error) {
      console.error("Erro ao migrar carteirinhas:", error);
      
      setResultado({
        success: false,
        message: "Erro ao migrar carteirinhas",
        details: [],
        errors: []
      });

      toast({
        title: "Erro na migração",
        description: "Não foi possível migrar as carteirinhas",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Agrupar erros por tipo para facilitar a análise
  const errosAgrupados: Record<string, ErroItem[]> = {};
  
  if (resultado?.errors && resultado.errors.length > 0) {
    resultado.errors.forEach((erro) => {
      const tipoErro = erro.erro.split('|')[0].trim();
      if (!errosAgrupados[tipoErro]) {
        errosAgrupados[tipoErro] = [];
      }
      errosAgrupados[tipoErro].push(erro);
    });
  }

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle>Migrar Carteirinhas UNIMED</CardTitle>
        <CardDescription>
          Migre os números de carteirinha com prefixo "0064" da tabela de pacientes para a tabela de carteirinhas, 
          associando-as ao plano UNIMED. Carteirinhas com outros prefixos serão ignoradas.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="tamanhoBatch" className="text-right">
              Tamanho do lote
            </Label>
            <Input
              id="tamanhoBatch"
              type="number"
              value={tamanhoBatch}
              onChange={(e) => setTamanhoBatch(parseInt(e.target.value) || 100)}
              min={1}
              max={1000}
              className="col-span-3"
            />
          </div>

          {resultado && (
            <div className={`p-4 rounded-md ${resultado.success ? "bg-green-50" : "bg-red-50"}`}>
              <h4 className="text-sm font-medium mb-1">
                {resultado.success ? "Migração concluída" : "Erro na migração"}
              </h4>
              <p className="text-sm">{resultado.message}</p>
              
              {resultado.errors && resultado.errors.length > 0 && (
                <Accordion type="single" collapsible className="mt-4">
                  <AccordionItem value="erros">
                    <AccordionTrigger className="text-sm">
                      Detalhes dos Erros ({resultado.errors.length})
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-4">
                        {Object.entries(errosAgrupados).map(([tipoErro, erros]) => (
                          <div key={tipoErro} className="border rounded-md p-3">
                            <h5 className="text-xs font-medium mb-2">{tipoErro} ({erros.length})</h5>
                            <ul className="text-xs space-y-1 max-h-40 overflow-y-auto">
                              {erros.slice(0, 10).map((erro, index) => (
                                <li key={index} className="border-b pb-1">
                                  <div><strong>Paciente:</strong> {erro.nome_paciente}</div>
                                  <div><strong>Carteirinha:</strong> {erro.numero_carteirinha}</div>
                                  <div><strong>Erro:</strong> {erro.erro}</div>
                                </li>
                              ))}
                              {erros.length > 10 && (
                                <li className="text-center italic">
                                  ... e mais {erros.length - 10} erros similares
                                </li>
                              )}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              )}
            </div>
          )}
        </div>
      </CardContent>
      <CardFooter className="flex justify-end">
        <Button
          onClick={handleMigrar}
          disabled={isLoading}
          className="gap-2"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Database className="h-4 w-4" />
          )}
          {isLoading ? "Migrando..." : "Iniciar Migração"}
        </Button>
      </CardFooter>
    </Card>
  );
} 