import os
from dotenv import load_dotenv
from supabase import create_client
from tabulate import tabulate

def get_table_statistics():
    load_dotenv()
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    if not (SUPABASE_URL and SUPABASE_KEY):
        print("Error: Missing Supabase credentials in .env file")
        return
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # 1. Processing Status Statistics
        print("\n=== Estatísticas Processing Status ===")
        ps_result = supabase.table("processing_status").select("*").execute()
        if ps_result.data:
            latest = ps_result.data[-1]  # Get most recent record
            ps_stats = [
                ["Total Registros", len(ps_result.data)],
                ["Total Guides", latest.get('total_guides', 0)],
                ["Processed Guides", latest.get('processed_guides', 0)],
                ["Total Execuções", latest.get('total_execucoes', 0)],
                ["Status", latest.get('status', 'N/A')],
                ["Task ID", latest.get('task_id', 'N/A')]
            ]
            print(tabulate(ps_stats, tablefmt="grid"))
        
        # 2. Guias Queue Statistics
        print("\n=== Estatísticas Guias Queue ===")
        queue_result = supabase.table("guias_queue").select("*").execute()
        if queue_result.data:
            # Count status types
            status_count = {}
            attempts_count = {}
            processed_null = 0
            
            for item in queue_result.data:
                status = item.get('status', 'unknown')
                attempts = item.get('attempts', 0)
                status_count[status] = status_count.get(status, 0) + 1
                attempts_count[attempts] = attempts_count.get(attempts, 0) + 1
                if item.get('processed_at') is None:
                    processed_null += 1
            
            queue_stats = [
                ["Total Registros", len(queue_result.data)],
                ["Registros Pendentes", status_count.get('pendente', 0)],
                ["Tentativas = 0", attempts_count.get(0, 0)],
                ["processed_at NULL", processed_null]
            ]
            print(tabulate(queue_stats, tablefmt="grid"))
            
            # Status distribution
            print("\nDistribuição de Status:")
            status_table = [[status, count] for status, count in status_count.items()]
            print(tabulate(status_table, headers=["Status", "Quantidade"], tablefmt="grid"))
        
        # 3. Execuções Statistics
        print("\n=== Estatísticas Execuções ===")
        exec_result = supabase.table("execucoes").select("*").execute()
        if exec_result.data:
            # Group by status_biometria if exists
            biometria_count = {}
            for item in exec_result.data:
                status = item.get('status_biometria', 'não informado')
                biometria_count[status] = biometria_count.get(status, 0) + 1
            
            exec_stats = [
                ["Total Registros", len(exec_result.data)]
            ]
            print(tabulate(exec_stats, tablefmt="grid"))
            
            if biometria_count:
                print("\nDistribuição de Status Biometria:")
                bio_table = [[status, count] for status, count in biometria_count.items()]
                print(tabulate(bio_table, headers=["Status", "Quantidade"], tablefmt="grid"))
        
    except Exception as e:
        print(f"\nError while fetching statistics: {str(e)}")

if __name__ == "__main__":
    get_table_statistics()
