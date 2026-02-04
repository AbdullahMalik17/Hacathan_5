import asyncio
import asyncpg
import os

async def init_db():
    url = "postgresql://neondb_owner:npg_Fe3fjcmZa4Ex@ep-still-waterfall-a8q7ziel-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    
    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    print(f"Connecting to Neon database...")
    try:
        conn = await asyncpg.connect(url)
        print("Connected! Executing schema...")
        
        # Split by ';' to execute in parts if needed, but asyncpg.execute handles blocks
        await conn.execute(schema_sql)
        
        print("✅ Database initialized successfully!")
        await conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
