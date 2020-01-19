import asyncio

import aiohttp
import base
from urllib.parse import urljoin
from lxml import html
from sgrequests import sgrequests
crawled = set()
headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }
flatten = lambda l: [item for sublist in l for item in sublist]
base_url = "https://www.acecashexpress.com/locations"
class Scrape(base.Spider):

    def crawl(self):
        session = sgrequests.SgRequests()
        states_provs = html.fromstring(session.get(base_url).text)
        locs = [urljoin(base_url, href) for href in
                states_provs.xpath('//ul[@class="states"]/li/a/@href[contains(., "/locations/")]')]
        loop = asyncio.get_event_loop()
        stores = []
        stores += loop.run_until_complete(self._fetch_all_states(set(locs), loop))

        return [s for s in stores if s]

    async def _fetch_state(self, session, url):
        async with session.get(url, timeout=60 * 60, headers=headers) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            cities_urls = [urljoin(base_url, s) for s in
                           sel.xpath('//ul[@class="cities-list"]/li/a/@href')]
            cities = await self._fetch_cities(session, cities_urls)
            return cities

    async def _fetch_cities(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_city(session, url)
            if res:
                results.append(res)
        return flatten(results)

    async def _fetch_city(self, session, url):
        async with session.get(url, timeout=60 * 60, headers=headers) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            last_page_ = sel.xpath('//ul[contains(@class, "pages")]/li[last()]/a/@href')
            if last_page_:
                urls = [url+'/page/{}'.format(str(href)) for href in range(1, int(last_page_[0].split('/')[-1]))]
            else:
                urls = [url+'/page/1']
            stores = await self._fetch_pages(session, urls)
            return stores

    async def _fetch_pages(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_page(session, url)
            if res:
                results.append(res)
        return flatten(results)

    async def _fetch_page(self, session, url):
        async with session.get(url, timeout=60 * 60, headers=headers) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            urls = [urljoin(url, s) for s in sel.xpath('//p[@class="location"]/a/@href[contains(., "locations/")]')]
            stores = await self._fetch_stores(session, urls)
            return stores

    async def _fetch_stores(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_store(session, url)
            if res:
                results.append(res)
        return results

    async def _fetch_all_states(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=5)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_state(session, url) for url in urls],
                    return_exceptions=False
                )
        return flatten(results)

    async def _fetch_store(self, session, url):
        if url.split('/')[-1] not in crawled:
            async with session.get(url, timeout=60 * 60, headers=headers) as response:
                resp = await response.text()
                location = html.fromstring(resp)
                i = base.Item(location)
                i.add_value('locator_domain', 'https://www.acecashexpress.com/locations')
                i.add_value('page_url', url)
                i.add_xpath('location_name', '//p[@class="store"]/span[@itemprop="name"]/text()', base.get_first)
                i.add_xpath('street_address', '//p[@class="store"]/span[@itemprop="streetAddress"]/text()',
                            base.get_first)
                i.add_xpath('city', '//p[@class="store"]/span[@itemprop="addressLocality"]/text()', base.get_first)
                i.add_xpath('state', '//p[@class="store"]/abbr[@itemprop="addressRegion"]/text()', base.get_first)
                i.add_xpath('zip', '//p[@class="store"]/span[@itemprop="postalCode"]/text()', base.get_first)
                i.add_value('country_code', base.get_country_by_code(i.as_dict().get('state')))
                i.add_xpath('phone', '//p[preceding-sibling::h4[1][contains(text(), "Phone")]]/a/text()', base.get_first, lambda x: "<MISSING>" if "()" in x else x)
                i.add_xpath('latitude', './/div/@data-latitude', lambda x: [s for s in x if s], base.get_first)
                i.add_xpath('store_number', './/div/@data-store', lambda x: [s for s in x if s], base.get_first)
                i.add_xpath('longitude', './/div/@data-longitude', lambda x: [s for s in x if s], base.get_first)
                i.add_value('hours_of_operation', '; '.join(
                    [' -'.join(s.xpath('.//text()')) for s in location.xpath('//ul[contains(@class, "hours")]/li')]))
                return i

if __name__ == '__main__':
    s = Scrape()
    s.run()
