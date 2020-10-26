import asyncio
import re
from pprint import pprint
from string import capwords

import aiohttp
import base
import lxml.html
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
urls = []
crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        try:
            async with session.get(url, timeout=20) as response:
                crawled.add(url)
                result = await response.json()
                i = base.Item(result)
                i.add_value('locator_domain', 'https://www.pella.com/window-door-showrooms/')
                i.add_value('page_url', 'https://www.pella.com/window-door-showrooms/'+result['webSite'])
                i.add_value('location_name', result['name'])
                i.add_value('phone', result['phone'])
                i.add_value('zip', result['zipCode'])
                i.add_value('state', result['state'])
                i.add_value('city', result['city'])
                i.add_value('street_address', ', '.join([s for s in [result.get('address1', ''),
                                                                     result.get('address2', '')] if
                                                         s != "null"]))
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                i.add_value('latitude', result['latitude'])
                i.add_value('longitude', result['longitude'])
                i.add_value('store_number', url.replace('https://api.pella.com/location/getpdsn/', '').replace('/',''))
                days = ['{} {}'.format(k.replace('hour', ''), v) for k, v in result['response'][0].items() if "hour" in k and k != "hourNote"]
                i.add_value('hours_of_operation', '; '.join(days))
                return i
        except asyncio.TimeoutError:
            return None

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=50)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return results

    def crawl(self):
        base_url = "https://www.pella.com/window-door-showrooms/"
        response = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        sitemap = response.content
        for sel in lxml.html.fromstring(sitemap).xpath('//div[@id="Content-StoreID"]//a/@href'):
            url = 'https://api.pella.com/location/getpdsn/{}'.format(sel.split('-')[-1])
            urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
