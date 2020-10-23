import re
from string import capwords

import base
import ast
from sgrequests import SgRequests
import json
import asyncio
import aiohttp
from urllib.parse import urljoin
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('staples_com')


base_url = "https://stores.staples.com/index.html"
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
            logger.info(url)
            i.add_xpath('location_name', '//h1[@class="Core-title"]/text()', base.get_first)
            i.add_xpath('store_number', '//div[@class="Core-storeId"]/text()', base.get_first, lambda x: x.replace('Store #', ''))
            i.add_xpath('phone', '//div[@id="phone-main"]/text()',
                        base.get_first, lambda x: x.strip())
            i.add_xpath('latitude', '//meta[@itemprop="latitude"]/@content', base.get_first, lambda x: x.strip())
            i.add_xpath('longitude', '//meta[@itemprop="longitude"]/@content', base.get_first, lambda x: x.strip())
            lat_lng = (i.as_dict()['latitude'], i.as_dict()['longitude'])
            i.add_xpath('city', '//address[@class="c-address"]//span[@class="c-address-city"]//text()', base.get_first,
                        lambda x: x.strip())
            i.add_xpath('street_address',
                        '//div[@class="Core-address"]//address[@class="c-address"]//span[@class="c-address-street-1" or @class="c-address-street-2"]/text()',
                        lambda x: ', '.join(x).strip())
            i.add_xpath('state', '//meta[@name="geo.region"]/@content', base.get_first, lambda x: x[x.find('-') + 1:])
            i.add_xpath('zip', '//address[@class="c-address"]//span[@class="c-address-postal-code"]/text()',
                        base.get_first, lambda x: x.strip(), lambda x: x.strip())
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']), lambda x: x.strip())
            i.add_xpath('hours_of_operation',
                        '//table[@class="c-hours-details"]//tr/@content',
                        lambda x: '; '.join(x), lambda x: x.strip())
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
            stores_urls = []
            all_s = sel.xpath('//h2[@class="Teaser-title"]/a/@href')
            if len(all_s) > 0:
                for s in all_s:
                    stores_urls.append(urljoin(base_url, s))
            else:
                if "coeur-dalene" in url:
                    url = "https://stores.staples.com/id/coeur-dalene/206-ironwood-dr"
                elif "baileys-crossroads" in url:
                    url = "https://stores.staples.com/va/baileys-crossroads/5801-leesburg-pike"
                stores_urls.append(url)
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
            for href in sel.xpath('//a[@class="Directory-listLink"]/@href'):
                sp = href.split('/')
                if len(sp) == 3:
                    href = sp[0]+'/'+sp[1]
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
        return flatten(results)

    def crawl(self):
        headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }
        requests = SgRequests()
        body = html.fromstring(requests.get(base_url, headers=headers).text)
        states = []
        for href in body.xpath('//a[@class="Directory-listLink"]/@href'):
            sp = href.split('/')
            if len(sp) == 3:
                href = sp[0]
            states.append(urljoin(base_url, href))
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(states, loop))
        return stores

if __name__ == '__main__':
    s = Scrape()
    s.run()
