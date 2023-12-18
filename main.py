import asyncio
from json import loads
from os.path import exists
from random import choice
from sys import stderr
from uuid import uuid4

import aiofiles
import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from loguru import logger
from pyuseragents import random as random_useragent

logger.remove()
logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')


async def main() -> None:
    while True:
        try:
            async with aiohttp.ClientSession(connector=ProxyConnector.from_url(url=choice(proxies_list))
                                             if proxies_list else None,
                                             headers={
                                                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                                                           'image/avif,image/webp,image/apng,'
                                                           '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                                                 'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7,cy;q=0.6',
                                                 'content-type': 'application/json',
                                                 'user-agent': random_useragent()
                                             }) as client:
                async with client.post(url='https://api.discord.gx.games/v1/direct-fulfillment',
                                       json={
                                           'partnerUserId': str(uuid4())
                                       },
                                       verify_ssl=False) as r:
                    token: str = loads(await r.text())['token']
                    nitro_url: str = f'https://discord.com/billing/partner-promotions/1180231712274387115/{token}'

                if short_url in ['y', 'yes']:
                    async with client.post(url='https://kurl.ru/shorten',
                                           data={
                                               'url': nitro_url
                                           },
                                           headers={
                                               'content-type': 'application/x-www-form-urlencoded',
                                           },
                                           verify_ssl=False) as r:
                        nitro_url: str = (await r.json())['data']['shorturl']

            async with aiofiles.open(file='tokens.txt',
                                     mode='a',
                                     encoding='utf-8-sig') as f:
                await f.write(f'{nitro_url}\n')

            logger.success(nitro_url)

        except Exception as error:
            logger.error(f'Unexpected Error: {error}')


async def wrapper() -> None:
    tasks: list = [asyncio.create_task(coro=main()) for _ in range(threads)]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    if exists(path='proxies.txt'):
        with open(file='proxies.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            proxies_list: list['str'] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]

    else:
        proxies_list: list[str] = []

    threads: int = int(input('Threads: '))
    short_url: str = input('Short URL? (y/yes | n/no): ').lower()
    print('')

    asyncio.run(wrapper())
