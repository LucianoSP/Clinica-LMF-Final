from pydantic_settings import BaseSettings
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do .env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    ANTHROPIC_API_KEY: str
    R2_ENDPOINT_URL: str | None = None
    R2_ACCESS_KEY_ID: str | None = None
    R2_SECRET_ACCESS_KEY: str | None = None
    R2_BUCKET_NAME: str | None = None
    R2_PUBLIC_URL_PREFIX: str | None = None
    GEMINI_API_KEY: str | None = None
    MISTRAL_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    JWT_SECRET: str | None = None
    JWT_EXPIRES_IN: str | None = None
    SUPABASE_JWT_SECRET: str | None = None
    SUPABASE_PASSWORD: str | None = None
    
    class Config:
        env_file = env_path
        extra = "ignore"  # Ignorar campos extras

# Instância global das configurações
settings = Settings()

# Cliente Supabase Síncrono global
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Função para obter cliente síncrono (usada em outras partes)
def get_supabase_client() -> Client:
    return supabase

# Função auxiliar para testar a conexão
def test_connection():
    if not supabase:
        print("Supabase (síncrono) não configurado")
        return False

    try:
        # Tenta fazer uma query simples
        response = supabase.table("pacientes").select("id", count="exact").limit(1).execute()
        print("Conexão com Supabase (síncrono) estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao conectar com Supabase (síncrono): {e}")
        return False
