import asyncio
import datetime
import sys

import aiohttp
import bs4

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


def open_file():
    with open('news_sites.txt', 'r') as file:
        for site in file:
            yield site


async def get_site(clean_url):
    url = f'https://{clean_url}'
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        try:
            async with session.get(url) as res:
                res.raise_for_status()
                return await res.text()
        except aiohttp.ClientConnectorError:
            print(f'Не удается получить доступ к сайту - {url}')
        except aiohttp.ClientResponseError:
            print(f'404 Not Found - {url}')


def get_title(html):
    if html is None:
        print('Empty page')
    else:
        bs = bs4.BeautifulSoup(html, 'html.parser')
        title = bs.select_one('title')
        if not title:
            return 'No title'
        return title.text.strip()


async def get_title_limit():
    start = datetime.datetime.now()
    tasks = []
    for site in open_file():
        site_with_correct_address = site[:site.index('\n')]
        tasks.append((1, site_with_correct_address, asyncio.create_task(get_site(site_with_correct_address))))
    for num, site_with_correct_address, task, in tasks:
        url = site_with_correct_address
        page = await task
        title = get_title(page)
        if title is not None:
            print(f'{url} - {title}', flush=True)
        else:
            print(f'{url} - No title')
    print(f'\nResult of time: {(datetime.datetime.now() - start).total_seconds()} seconds')


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_title_limit())
