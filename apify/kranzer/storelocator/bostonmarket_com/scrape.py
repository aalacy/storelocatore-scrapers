import re
from string import capwords

import base
import ast
import requests, json
import asyncio
import aiohttp
from lxml import html
base_url = "https://www.bostonmarket.com/location/"
flatten = lambda l: [item for sublist in l for item in sublist]


class Scrape(base.Spider):
    crawled = set()
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60) as response:
            resp = await response.text()
            res_sel = html.fromstring(resp)
            i = base.Item(res_sel)
            i.add_value('locator_domain', base_url)
            i.add_value('page_url', url)
            i.add_xpath('location_name', '//div[contains(@class, "Core-info")]', lambda x: x[0] if len(x) > 0 else None, lambda x: x.xpath('./h1/text() | ./div[@class="Core-location"]/text()') if x else None, lambda x: ', '.join(x) if x else None)
            i.add_xpath('phone', '(//div[@id="phone-main"])[1]/text()', base.get_first)
            i.add_xpath('latitude', '//meta[@itemprop="latitude"]/@content', base.get_first)
            i.add_xpath('longitude', '//meta[@itemprop="longitude"]/@content', base.get_first)
            lat_lng = (i.as_dict()['latitude'], i.as_dict()['longitude'])
            i.add_xpath('city', '//meta[@itemprop="addressLocality"]/@content', base.get_first)
            i.add_xpath('street_address', '//meta[@itemprop="streetAddress"]/@content', base.get_first)
            i.add_xpath('state', '//abbr[@itemprop="addressRegion"]/text()', base.get_first)
            i.add_xpath('zip', '//span[@itemprop="postalCode"]/text()', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('store_number', '//div[@class="Core-id"]/text()', base.get_first, lambda x: x.replace('Store: #', ''))
            i.add_xpath('hours_of_operation', '//table[@class="c-hours-details"]//tr[@itemprop="openingHours"]/@content', lambda x: '; '.join(x))
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
        async with session.get(url, timeout=60) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            stores_urls = ["https://www.bostonmarket.com/location/"+s.replace('../','') for s in sel.xpath('//a[@class="Teaser-titleLink"]/@href')]
            stores = await self._fetch_stores(session, stores_urls)
            return stores

    async def _fetch_cities(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_city(session, url)
            results.append(res)
        return flatten(results)

    async def _fetch_state(self, session, url):
        async with session.get(url, timeout=60) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            cities_urls = []
            for href in sel.xpath('//a[@class="Directory-listLink"]/@href'):
                sp = href.replace('../','').split('/')
                if len(sp) == 3:
                    href = sp[0]+'/'+sp[1]
                cities_urls.append("https://www.bostonmarket.com/location/"+href)
            cities = await self._fetch_cities(session, cities_urls)
            return cities

    async def _fetch_all_states(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=20)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_state(session, url) for url in urls],
                    return_exceptions=False
                )
        return flatten(results)

    def crawl(self):
        headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }
        body = html.fromstring(requests.get(base_url, headers=headers).text)
        states = []
        for href in body.xpath('//a[@class="Directory-listLink"]/@href'):
            sp = href.replace('../','').split('/')
            if len(sp) == 3:
                href = sp[0]
            states.append("https://www.bostonmarket.com/location/"+href)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return stores

if __name__ == '__main__':
    s = Scrape()
    s.run()
