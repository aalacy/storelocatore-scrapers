import re
from string import capwords

import base
import ast
import requests, json
import asyncio
import aiohttp
from urllib.parse import urljoin
from lxml import html
base_url = "https://www.aspendental.com/find-an-office"
flatten = lambda l: [item for sublist in l for item in sublist]


class Scrape(base.Spider):
    crawled = set()
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            res_sel = html.fromstring(resp)
            i = base.Item(res_sel)
            coords = res_sel.xpath('(//a[contains(@href, "maps/")])[1]/@href')
            if coords:
                coords_ = coords[0].split('/')[-1]
                if ',' in coords_:
                    i.add_value('locator_domain', base_url)
                    i.add_value('page_url', url)
                    i.add_xpath('phone', '(//div[@class="ssa-phone-number"])[1]/a/span/text()', base.get_first, lambda x: x.strip())
                    i.add_value('latitude', coords_.split(',')[0])
                    i.add_value('longitude', coords_.split(',')[1])
                    lat_lng = (i.as_dict()['latitude'], i.as_dict()['longitude'])
                    i.add_xpath('city', '//meta[@property="business__contact_data__street_address"]/@content', base.get_first)
                    i.add_xpath('street_address', '//meta[@property="business__contact_data__street_address"]/@content', base.get_first)
                    i.add_xpath('state', '//meta[@property="business__contact_data__region"]/@content', base.get_first)
                    i.add_xpath('zip', '//meta[@property="business__contact_data__postal_code"]/@content', base.get_first)
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']), lambda x: x.strip())
                    js_ = res_sel.xpath('(//script[@type="application/ld+json"])[last()]/text()')[0]
                    js = json.loads(js_)
                    hours = []
                    for h in js.get('openingHoursSpecification', []):
                        for d in h.get('dayOfWeek',[]):
                            st = ""
                            st+="{} - {}-{}".format(d, h.get('opens'), h.get('closes'))
                            hours.append(st)
                    i.add_value('hours_of_operation', '; '.join(hours))
                    i.add_value('phone', js['telephone'])
                    i.add_value('location_name', js['name'])
                    i.add_value('location_type', js['@type'])
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
            stores_urls = [urljoin(base_url, s) for s in sel.xpath('(//div[@class="collection-wrapper"])[1]//a/@href')]
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
            cities_urls = []
            for href in sel.xpath('(//div[@class="collection-wrapper"])[1]//a/@href'):
                cities_urls.append(urljoin(base_url, href))
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
        states = []
        for href in body.xpath('(//div[@class="collection-wrapper"])[1]//a/@href'):
            states.append(urljoin(base_url, href))
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return stores

if __name__ == '__main__':
    s = Scrape()
    s.run()
