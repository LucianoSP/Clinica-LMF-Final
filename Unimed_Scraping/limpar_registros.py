import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

def clear_tables():
    load_dotenv()
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    if not (SUPABASE_URL and SUPABASE_KEY):
        print("Error: Missing Supabase credentials in .env file")
        return
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # 1. Clear execucoes table with a WHERE clause
        print("Deleting records from execucoes table...")
        result = supabase.table("execucoes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"Deleted {len(result.data) if result.data else 0} records from execucoes")
        
        # 2. Clear guias_queue table
        print("\nDeleting records from guias_queue table...")
        result = supabase.table("guias_queue").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"Deleted {len(result.data) if result.data else 0} records from guias_queue")
        
        # 3. Clear processing_status table
        print("\nDeleting records from processing_status table...")
        result = supabase.table("processing_status").delete().neq("task_id", "none").execute()
        print(f"Deleted {len(result.data) if result.data else 0} records from processing_status")
        
        print("\nAll tables cleared successfully!")
        
    except Exception as e:
        print(f"\nError while clearing tables: {str(e)}")

if __name__ == "__main__":
    clear_tables()
