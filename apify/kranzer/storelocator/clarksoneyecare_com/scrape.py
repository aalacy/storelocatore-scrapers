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
crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = lxml.html.fromstring(resp)
            i = base.Item(sel)
            i.add_value('locator_domain', 'https://www.clarksoneyecare.com/locations/')
            i.add_value('page_url', url)
            i.add_xpath('location_name', '//h1[@class="location-name"]/text()', base.get_first)
            i.add_xpath('phone', '//div[@class="phone-number"]/a/text()', base.get_first)
            i.add_xpath('street_address', '//address[@id="prgmStoreAddress"]/text()',
                        base.get_first, lambda x: x.strip())
            ct = sel.xpath('//address[@id="prgmStoreAddress"]/text()')[-1]
            tup = re.findall(r'(.+?),\s+?([A-Z]+)\s+(\d+)', ct)
            if tup:
                i.add_value('city', tup[0][0])
                i.add_value('state', tup[0][1], lambda x: x.upper())
                i.add_value('zip', tup[0][2])
                i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('hours_of_operation', '//div[contains(@class, "day")]',
                        lambda x: [' '.join(s.xpath('.//text()')) for s in x],
                        lambda x: '; '.join([re.sub(r'\s+', ' ', s.replace('\n', '').strip()) for s in x]))
            i.add_xpath('latitude', '//div[@class="marker"]/@data-lat', base.get_first)
            i.add_xpath('longitude', '//div[@class="marker"]/@data-lng', base.get_first)
            coords = (i.as_dict()['latitude'], i.as_dict()['longitude'])
            if coords not in crawled:
                crawled.add(coords)
                return i

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return results

    def crawl(self):
        base_url = "https://www.clarksoneyecare.com/locations-sitemap.xml"
        response = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        sitemap = response.content
        urls = []
        for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            if not url.endswith('locations/'):
                urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
