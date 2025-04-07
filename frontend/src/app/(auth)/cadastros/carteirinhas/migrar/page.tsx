"use client";

import { MigrarCarteirinhas } from "@/components/carteirinhas/migrar-carteirinhas";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import Link from "next/link";

export default function MigrarCarteirinhasPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-semibold text-slate-900">Migrar Carteirinhas UNIMED</h1>
          <Link 
            href="/cadastros/carteirinhas" 
            className="flex items-center text-sm text-muted-foreground hover:text-slate-900 transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
            Voltar para Carteirinhas
          </Link>
        </div>
        <p className="text-slate-500">
          Migre os números de carteirinha com prefixo "0064" da tabela de pacientes para a tabela de carteirinhas, 
          associando-as ao plano UNIMED. Carteirinhas com outros prefixos serão ignoradas.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center py-8">
        <MigrarCarteirinhas />
      </div>
    </div>
  );
} 