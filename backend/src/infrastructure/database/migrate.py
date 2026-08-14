import asyncio
import os
import sys

# Add src to the path so modules can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.infrastructure.database.connection import init_db

async def main():
    print("Iniciando migración a Supabase...")
    try:
        await init_db()
        print("Tablas creadas exitosamente.")
    except Exception as e:
        print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    asyncio.run(main())
