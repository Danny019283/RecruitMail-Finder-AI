import asyncio

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
