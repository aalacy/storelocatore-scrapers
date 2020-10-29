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

logger = SgLogSetup().get_logger('mavistire_com')


crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = lxml.html.fromstring(resp)
            i = base.Item(sel)
            i.add_value('locator_domain', 'https://www.mavistire.com/locations/')
            i.add_value('page_url', url)
            i.add_xpath('location_name', '//h1/text()', base.get_first)
            i.add_xpath('phone', '//span[@itemprop="telephone"]/text()', base.get_first)
            i.add_xpath('street_address', '//span[@itemprop="streetAddress"]/text()', base.get_first, lambda x: x.strip())
            i.add_xpath('city', '//span[@itemprop="addressLocality"]/text()', base.get_first)
            i.add_xpath('state', '//span[@itemprop="addressRegion"]/text()', base.get_first)
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            i.add_xpath('zip', '//span[@itemprop="postalCode"]/text()', base.get_first)
            i.add_xpath('hours_of_operation', '//span[@itemprop="openingHours"]/text()', lambda x: '; '.join(x))
            coords_sc = sel.xpath('//script/text()[contains(., "Lat")]')
            if coords_sc:
                i.add_value('latitude', coords_sc[0], lambda x: x[x.find('Lat:')+4:], lambda x: x[:x.find(',')])
                i.add_value('longitude', coords_sc[0], lambda x: x[x.find('Lng:')+4:], lambda x: x[:x.find(',')])
                i.add_value('store_number', coords_sc[0], lambda x: x[x.find('Store:')+6:], lambda x: x[:x.find(',')], lambda x: x.replace('\'',''))
                coords = (i.as_dict()['latitude'], i.as_dict()['longitude'])
                if coords not in crawled:
                    crawled.add(coords)
                    logger.info(i)
                    return i

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return results

    def crawl(self):
        base_url = "https://www.mavistire.com/locations/"
        response = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        sitemap = response.content
        urls = []
        for sel in lxml.html.fromstring(sitemap).xpath('//tr/td[last()]/a[contains(text(), "hours")]/@href'):
            url = urljoin(base_url, sel)
            urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
