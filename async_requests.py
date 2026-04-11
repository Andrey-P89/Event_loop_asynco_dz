import asyncio
import datetime
import aiohttp

from itertools import batched
from sqlalchemy import text

from db import DbSession, open_orm, close_orm, Person

MAX_REQUESTS = 10
TOTAL_PEOPLE = 82

async def get_total_people_count(http_session: aiohttp.ClientSession) -> int:
    response = await http_session.get(f'https://swapi.dev/api/people/')
    data = await response.json()
    return data.get('count', 0)


async def get_person(person_id: int, http_session: aiohttp.ClientSession):
    response = await http_session.get(f'https://swapi.dev/api/people/{person_id}/')

    if response.status != 200:
        return None

    json_data = await response.json()
    person_data = {
        'id': person_id,
        'name': json_data.get('name'),
        'birth_year': json_data.get('birth_year'),
        'eye_color': json_data.get('eye_color'),
        'gender': json_data.get('gender'),
        'hair_color': json_data.get('hair_color'),
        'skin_color': json_data.get('skin_color'),
        'height': json_data.get('height'),
        'mass': json_data.get('mass'),
        'homeworld': json_data.get('homeworld'),
    }
    return person_data

async def insert_result(result: list[dict]):
    valid_data = [d for d in result if d is not None]

    async with DbSession() as session:
        people_objects = [Person(**data) for data in valid_data]
        session.add_all(people_objects)
        await session.commit()


async def main():
    await open_orm()
    async with aiohttp.ClientSession() as aiohttp_session:
        async with DbSession() as session:
            await session.execute(text("TRUNCATE TABLE people RESTART IDENTITY;"))
            await session.commit()

        # Почему-то программа зависает
        # total = await get_total_people_count(aiohttp_session)

        for batch in batched(range(1, TOTAL_PEOPLE + 1), MAX_REQUESTS):
            print("Поезали")
            coros = [get_person(i, aiohttp_session) for i in batch]
            result = await asyncio.gather(*coros)
            insert_result_task = asyncio.create_task(insert_result(result))
        tasks = asyncio.all_tasks()
        current_task = asyncio.current_task()
        tasks.remove(current_task)
        for task in tasks:
            await task
    await close_orm()

start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)