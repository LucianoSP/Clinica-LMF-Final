// components/auditoria/AuditoriaHeader.tsx
import React from 'react';
import { Files, AlertCircle, Calendar, FileText } from 'lucide-react';
import { format } from 'date-fns';
import { Card } from "@/components/ui/card";
import { CardContent } from "@/components/ui/card";
import { CardHeader } from "@/components/ui/card";
import { CardTitle } from "@/components/ui/card";
import { AuditoriaResultado } from "@/types/auditoria";

const formatarData = (data: string) => {
    if (!data) return '-';
    try {
        return new Date(data).toLocaleDateString('pt-BR');
    } catch {
        return data;
    }
};

export const AuditoriaHeader = () => {
    return (
        <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold tracking-tight">
                Auditoria de Execuções
            </h1>
            <p className="text-sm text-muted-foreground">
                Gerencie e monitore as divergências encontradas
            </p>
        </div>
    );
};