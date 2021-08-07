import aiohttp
import asyncio


async def test():
    session = aiohttp.ClientSession()
    m = 100
    res = await asyncio.gather(*[session.get("http://localhost:8000/random") for i in range(m)])
    txts = await asyncio.gather(*[r.json() for r in res])
    print('\n'.join(txts[i]["data"][-26:] for i in range(m)))
    await session.close()

asyncio.get_event_loop().run_until_complete(test())