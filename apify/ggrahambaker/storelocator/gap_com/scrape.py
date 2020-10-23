import re
from string import capwords

import base
import ast
import requests, json
import asyncio
import aiohttp
from urllib.parse import urljoin
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gap_com')


base_url = "https://www.gap.com/stores/"
flatten = lambda l: [item for sublist in l for item in sublist]
class Scrape(base.Spider):
    crawled = set()

    def normalize_days(self, text):
        text = text.replace('Mo ', 'Mon ')
        text = text.replace('Tu ', 'Tue ')
        text = text.replace('We ', 'Wed ')
        text = text.replace('Th ', 'Thu ')
        text = text.replace('Fr ', 'Fri ')
        text = text.replace('Sa ', 'Sat ')
        text = text.replace('Su ', 'Sun ')
        return text

    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            res_sel = html.fromstring(resp)
            js = res_sel.xpath('//script[@type="application/ld+json"]/text()')[0]
            js = re.sub(r'<span.+?=".+?">', '', js)
            js = re.sub(r'</span>', '', js)
            js = re.sub(r' <br />', '; ', js)
            json_resp = json.loads(js)[0]
            i = base.Item(json_resp)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', url)
            i.add_value('phone', json_resp['address']['telephone'])
            i.add_value('location_type', json_resp['@type'])
            lat_lng = (json_resp['geo']['latitude'], json_resp['geo']['longitude'])
            i.add_value('latitude', lat_lng[0])
            i.add_value('longitude', lat_lng[1])
            i.add_value('city', json_resp['address']['addressLocality'], lambda x: capwords(x))
            i.add_value('street_address', json_resp['address']['streetAddress'])
            i.add_value('state', json_resp['address']['addressRegion'])
            i.add_value('zip', json_resp['address']['postalCode'])
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            store_num = url[url.find('/gap-'):].replace('/gap-', '').replace('.html', '')
            i.add_value('location_name', json_resp['name'], lambda x: x.split(' |')[0], lambda x: x+' Store #'+store_num)
            i.add_value('store_number', store_num)
            i.add_value('hours_of_operation', json_resp['openingHours'], lambda x: self.normalize_days(x))
            if store_num not in self.crawled:
                self.crawled.add(store_num)
                return i

    async def _fetch_stores(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_store(session, url)
            if res:
                results.append(res)
        return results
        # logger.info(res)
        # logger.info(results)
        # return res

    async def _fetch_city(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            stores_urls = [urljoin(base_url, s) for s in sel.xpath('//a[contains(@class, "view-store")]/@href')]
            stores = await self._fetch_stores(session, stores_urls)
            return stores

    async def _fetch_cities(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_city(session, url)
            results.append(res)
        return flatten(results)

    async def _fetch_state(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            cities_urls = [urljoin(base_url, s) for s in sel.xpath('//li[@role="listitem"]/div/a/@href')]
            cities = await self._fetch_cities(session, cities_urls)
            return cities

    async def _fetch_all_states(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_state(session, url) for url in urls],
                    return_exceptions=True
                )
        return flatten(results)

    def crawl(self):
        headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }
        body = html.fromstring(requests.get(base_url, headers=headers).text)
        states = [urljoin(base_url, s) for s in body.xpath('//li[@role="listitem"]/div/a/@href')]
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return stores

if __name__ == '__main__':
    s = Scrape()
    s.run()
