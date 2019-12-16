import re
from string import capwords

import base
import ast
import requests, json
import asyncio
import aiohttp
from urllib.parse import urljoin
from lxml import html
base_url = "https://locations.massageenvy.com/index.html"
flatten = lambda l: [item for sublist in l for item in sublist]


class Scrape(base.Spider):
    crawled = set()
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            res_sel = html.fromstring(resp)
            i = base.Item(res_sel)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', url)
            i.add_xpath('location_name', '//h1[@class="info-h1"]//span//text()', lambda x: '- '.join(x), lambda x: x.strip())
            i.add_xpath('phone', './/span[@id="telephone"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('latitude', '//meta[@itemprop="latitude"]/@content', base.get_first, lambda x: x.strip())
            i.add_xpath('longitude', '//meta[@itemprop="longitude"]/@content', base.get_first, lambda x: x.strip())
            lat_lng = (i.as_dict()['latitude'], i.as_dict()['longitude'])
            i.add_xpath('city', '//address[@class="c-address"]//span[@class="c-address-city"]/span[@itemprop="addressLocality"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('street_address', '//address[@class="c-address"]//span[@class="c-address-street-1"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('state', '//address[@class="c-address"]//abbr[@class="c-address-state"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('zip', '//address[@class="c-address"]//span[@class="c-address-postal-code"]/text()', base.get_first, lambda x: x.strip(), lambda x: x.strip())
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']), lambda x: x.strip())
            i.add_xpath('hours_of_operation', '//table[@class="c-location-hours-details"]//tr[td]', lambda x: '; '.join([' '.join(s.xpath('.//text()')) for s in x]), lambda x: x.replace('  ', ' ').strip())
            if lat_lng not in self.crawled:
                self.crawled.add(lat_lng)
                print(i)
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
            stores_urls = [urljoin(base_url, s) for s in sel.xpath('//a[@class="location-title-link"]/@href')]
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
            for href in sel.xpath('//a[@class="c-directory-list-content-item-link"]/@href'):
                sp = href.split('/')
                if len(sp) == 3:
                    href = sp[0]+'/'+sp[1] + '.html'
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
        for href in body.xpath('//a[@class="c-directory-list-content-item-link"]/@href'):
            sp = href.split('/')
            if len(sp) == 3:
                href = sp[0] + '.html'
            states.append(urljoin(base_url, href))
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return stores

if __name__ == '__main__':
    s = Scrape()
    s.run()
