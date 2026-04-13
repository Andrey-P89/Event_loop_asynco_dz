import asyncio
import datetime
import aiohttp

from db import DbSession, Person


MAX_REQUESTS = 10

def batched(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]

async def get_total_people_count(http_session: aiohttp.ClientSession) -> int:
    url = 'https://swapi.dev/api/people/'
    try:
        response = await http_session.get(url)
        if response.status != 200:
            print(f'Ошибка {response.status} при запросе {url}')
            return 0   
        data = await response.json()
        return data.get('count', 0)
            
    except aiohttp.ClientError:
        print(f'Сетевая ошибка при запросе {url}')
        return 0
    except asyncio.TimeoutError:
        print(f'Таймаут при запросе {url}')
        return 0


async def get_name_homeworld(url: str, http_session: aiohttp.ClientSession):
    try:
        response = await http_session.get(url)
        if response.status != 200:
            return None
        json_data = await response.json()
        name_homeworld = json_data.get('name')
        return name_homeworld
    except aiohttp.ClientError:
        print(f'Сетевая ошибка при запросе {url}')
        return None
    except asyncio.TimeoutError:
        print(f'Таймаут при запросе {url}')
        return None


async def get_person(person_id: int, http_session: aiohttp.ClientSession):
    url = f'https://swapi.dev/api/people/{person_id}/'
    try:
        response = await http_session.get(url)
        if response.status != 200:
            return None
        json_data = await response.json()

        homeworld_url = json_data.get('homeworld')
        if homeworld_url:
            homeworld = await get_name_homeworld(homeworld_url, http_session)
        else:
            homeworld = None

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
            'homeworld': homeworld
        }
        return person_data
    except aiohttp.ClientError:
        print(f'Сетевая ошибка при запросе {url}')
        return None
    except asyncio.TimeoutError:
        print(f'Таймаут при запросе {url}')
        return None

async def insert_result(result: list[dict]):
    valid_data = [d for d in result if d is not None]

    if not valid_data:
        return

    async with DbSession() as session:
        people_objects = [Person(**data) for data in valid_data]
        session.add_all(people_objects)
        try:
            await session.commit()
        except Exception as e:
            print(f"Ошибка при вставке в БД: {e}")
            await session.rollback()


async def main():
    insert_tasks = []
    async with aiohttp.ClientSession() as aiohttp_session:
        total = await get_total_people_count(aiohttp_session)
        for batch in batched(range(1, total + 1), MAX_REQUESTS):
            coros = [get_person(i, aiohttp_session) for i in batch]
            result = await asyncio.gather(*coros)
            insert_tasks.append(asyncio.create_task(insert_result(result)))
        await asyncio.gather(*insert_tasks)

start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)