import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { taskId, dataInicial, dataFinal, maxGuias } = body;

    if (!taskId || !dataInicial || !dataFinal) {
      return NextResponse.json(
        { error: 'taskId, dataInicial e dataFinal são obrigatórios' },
        { status: 400 }
      );
    }

    // Caminho para o script Python (ajustado para o caminho correto)
    const scriptPath = path.resolve(process.cwd(), '../Unimed_Scraping/todas_as_fases_adaptado.py');
    
    // Comando para executar o script Python com os parâmetros
    const command = `python "${scriptPath}" --start_date="${dataInicial}" --end_date="${dataFinal}" ${maxGuias ? `--max_guides=${maxGuias}` : ''}`;
    
    console.log(`Executando comando: ${command}`);

    // Executar o script Python em segundo plano
    const childProcess = exec(command, {
      maxBuffer: 1024 * 1024 * 10, // 10MB buffer
    });
    
    // Registrar saída do processo (opcional, para debug)
    childProcess.stdout?.on('data', (data) => {
      console.log(`[Python stdout]: ${data}`);
    });
    
    childProcess.stderr?.on('data', (data) => {
      console.error(`[Python stderr]: ${data}`);
    });
    
    // Não esperamos o processo terminar, pois ele pode demorar muito
    // Apenas retornamos uma resposta imediata
    
    return NextResponse.json({ 
      success: true, 
      message: 'Processo de captura iniciado em segundo plano',
      taskId
    });
    
  } catch (error) {
    console.error('Erro ao processar requisição:', error);
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    );
  }
} 