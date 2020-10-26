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
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hooters_com')


urls = []
crawled = set()

flatten = lambda l: [item for sublist in l for item in sublist]

class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        try:
            async with session.get(url, timeout=20) as response:
                results = await response.json()
                items = []
                r_ = results.get('locations', [])
                if r_:
                    for result in r_:
                        i = base.Item(result)
                        i.add_value('locator_domain', 'https://www.hooters.com/locations/')
                        i.add_value('page_url', 'https://www.hooters.com'+result['detailsUrl'])
                        i.add_value('location_name', result['name'])
                        i.add_value('phone', result['phone'])
                        ct = result['address']['line-2']
                        tup = re.findall(r'(.+?),\s?([A-Z]+)\s(\d+)', ct)
                        if tup:
                            i.add_value('city', tup[0][0])
                            i.add_value('state', tup[0][1], lambda x: x.upper())
                            i.add_value('zip', tup[0][2])
                            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                        i.add_value('street_address', result['address']['line-1'])
                        i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                        i.add_value('latitude', result['latitude'])
                        i.add_value('longitude', result['longitude'])
                        i.add_value('store_number', result['id'])
                        hrs = result.get('hours', {})
                        if hrs:
                            days = ['{} {} - {}'.format(capwords(k), v.get('open'), v.get('close')) for k, v in hrs.items()]
                            i.add_value('hours_of_operation', '; '.join(days))
                        items.append(i)
                return items
        except asyncio.TimeoutError:
            return None

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=50)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return flatten(results)

    def crawl(self):
        for sel in base.us_states_codes.union(base.ca_provinces_codes):
            url = 'https://www.hooters.com/api/search_locations.json?address={}'.format(sel)
            urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
