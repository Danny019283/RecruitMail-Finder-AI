import asyncio
import os
import sys

# Add src to the path so modules can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.infrastructure.database.connection import recreate_db

async def main():
    print("Iniciando migración a Supabase (recreando tablas)...")
    try:
        await recreate_db()
        print("Tablas recreadas exitosamente con la nueva estructura.")
    except Exception as e:
        print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    asyncio.run(main())
