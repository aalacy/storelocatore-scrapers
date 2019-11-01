import re
from string import capwords

import base
import ast
import requests, json
import asyncio
import aiohttp
from urllib.parse import urljoin
from lxml import html
base_url = "https://locations.grandluxcafe.com/"
flatten = lambda l: [item for sublist in l for item in sublist]
class Scrape(base.Spider):
    crawled = set()
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            res_sel = html.fromstring(resp)
            js = res_sel.xpath('//script[@type="application/ld+json"]/text()')[1]
            js = re.sub(r'<span.+?=".+?">', '', js)
            js = re.sub(r'</span>', '', js)
            js = re.sub(r' <br />', '; ', js)
            json_resp = json.loads(js)
            i = base.Item(json_resp)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', url)
            i.add_value('location_name', json_resp.get('name',''))
            i.add_value('phone', json_resp.get('telephone',''))
            i.add_value('location_type', json_resp.get('@type',''))
            lat_lng = (json_resp.get('geo',{}).get('latitude', ''), json_resp.get('geo', {}).get('longitude',''))
            i.add_value('latitude', lat_lng[0])
            i.add_value('longitude', lat_lng[1])
            i.add_value('city', json_resp.get('address',{}).get('addressLocality',''), lambda x: capwords(x))
            i.add_value('street_address', json_resp.get('address',{}).get('streetAddress',''))
            i.add_value('state', json_resp.get('address',{}).get('addressRegion', ''))
            i.add_value('zip', json_resp.get('address',{}).get('postalCode',''))
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_value('store_number', url.split('/')[-2])
            i.add_value('hours_of_operation', res_sel.xpath('//table[@class="time-table"]//tr'), lambda x: [' '.join(s.xpath('./td/text()')) for s in x], lambda x: '; '.join([s for s in x if s.strip()]))
            if lat_lng not in self.crawled:
                self.crawled.add(lat_lng)
                return i

    async def _fetch_stores(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_store(session, url)
            if res:
                results.append(res)
        return results

    async def _fetch_city(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            stores_urls = [urljoin(base_url, s) for s in sel.xpath('//div[@class="content-split"]/p/a/@href')]
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
            cities_urls = [urljoin(base_url, s) for s in sel.xpath('//div[@class="content-split"]/p/a/@href')]
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
        states = [urljoin(base_url, s) for s in body.xpath('//div[@class="breadcrumbs"]/a/@href')]
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return stores

if __name__ == '__main__':
    s = Scrape()
    s.run()
