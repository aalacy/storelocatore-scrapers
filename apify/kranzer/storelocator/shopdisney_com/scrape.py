import re
from string import capwords

import base
import ast
import requests, json
import asyncio
import aiohttp
from urllib.parse import urljoin
from lxml import html
import sgrequests

base_url = "https://stores.shopdisney.com/"
flatten = lambda l: [item for sublist in l for item in sublist]
headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
            "Connection":"close"
        }

class Scrape(base.Spider):
    retries = 0
    crawled = set()
    async def _fetch_store(self, session, url):
        try:
            async with session.get(url, timeout=60 * 60, headers=headers) as response:
                resp = await response.text()
                res_sel = html.fromstring(resp)
                i = base.Item(res_sel)
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', url)
                i.add_xpath('location_name', '//h1[@class="toptitle"]/text()', base.get_first)
                i.add_xpath('phone', '//span[@itemprop="telephone"]/text()', base.get_first)
                i.add_xpath('latitude', '//meta[@property="place:location:latitude"]/@content', base.get_first)
                i.add_xpath('longitude', '//meta[@property="place:location:longitude"]/@content', base.get_first)
                lat_lng = (i.as_dict()['latitude'], i.as_dict()['longitude'])
                i.add_xpath('city', '//span[@itemprop="addressLocality"]/text()', base.get_first)
                i.add_xpath('street_address', '//div[@itemprop="streetAddress"]/text()', base.get_first)
                i.add_xpath('state', '//span[@itemprop="addressRegion"]/text()', base.get_first)
                i.add_xpath('zip', '//span[@itemprop="postalCode"]/text()', base.get_first, lambda x: x.strip())
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                i.add_value('store_number', url.split('/')[-2])
                i.add_xpath('hours_of_operation', '//table[@id="poihours"]//tr',
                            lambda x: '; '.join([s.xpath('./td[1]/text()')[0] + ' - ' + s.xpath('./td[2]/text()')[0] for s in x]))
                if lat_lng not in self.crawled:
                    self.crawled.add(lat_lng)
                    return i
        except:
            return None

    async def _fetch_stores(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_store(session, url)
            if res:
                results.append(res)
        return [s for s in results if s]

    async def _fetch_city(self, session, url):
        try:
            if self.retries < 8:
                async with session.get(url, timeout=60 * 60, headers=headers) as response:
                    resp = await response.text()
                    sel = html.fromstring(resp)
                    stores_urls = [urljoin(base_url, s) for s in sel.xpath('//a[@class="contentlist_item"]/@href')]
                    stores = await self._fetch_stores(session, stores_urls)
                    return stores
        except:
            self.retries += 1
            return self._fetch_city(session=session, url=url)


    async def _fetch_cities(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_city(session, url)
            results.append(res)
        return [s for s in flatten(results) if s]

    async def _fetch_state(self, session, url):
        async with session.get(url, timeout=60 * 60, headers=headers) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            cities_urls = []
            for href in sel.xpath('//a[@class="contentlist_item"]/@href'):
                cities_urls.append(urljoin(base_url, href))
            cities = await self._fetch_cities(session, cities_urls)
            return cities

    async def _fetch_all_states(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_state(session, url) for url in urls],
                    return_exceptions=False
                )
        return [s for s in flatten(results) if s]

    def crawl(self):
        session = sgrequests.SgRequests()
        body = html.fromstring(session.get(base_url, headers=headers).text)
        states = []
        for href in body.xpath('//a[@class="contentlist_item"]/@href'):
            states.append(urljoin(base_url, href))
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return [s for s in stores if s]

if __name__ == '__main__':
    s = Scrape()
    s.run()
