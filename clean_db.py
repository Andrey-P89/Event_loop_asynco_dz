import asyncio
from sqlalchemy import text
from db import DbSession

async def clean():
    async with DbSession() as session:
        await session.execute(text("TRUNCATE TABLE people RESTART IDENTITY;"))
        await session.commit()
        print("Таблица очищена")

if __name__ == '__main__':
    asyncio.run(clean())