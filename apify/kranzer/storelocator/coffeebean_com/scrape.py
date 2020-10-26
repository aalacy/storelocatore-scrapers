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
            i.add_value('locator_domain', 'https://www.coffeebean.com/store-locator')
            i.add_value('page_url', url)
            i.add_xpath('location_name', '//h1//text()', base.get_first, lambda x: re.sub(r'\s+', ' ', x.strip()))
            i.add_xpath('street_address', './/div[@class="address-group"]/span[@property="streetAddress"]/text()',
                        base.get_first, lambda x: x.strip())
            i.add_xpath('city', './/div[@class="address-group"]/span[@property="addressLocality"]/text()',
                        base.get_first)
            i.add_xpath('state', '//div[@class="address-group"]/span[@property="addressRegion"]/text()', base.get_first)
            i.add_xpath('zip', '//div[@class="address-group"]/span[@property="postalCode"]/text()', base.get_first)
            i.add_xpath('country_code', '//div[@class="address-group"]/span[@property="addressCountry"]/text()',
                        base.get_first)
            i.add_xpath('hours_of_operation', '//div[preceding-sibling::div[1][contains(text(), "Hours")]]/div',
                        lambda x: [' '.join(s.xpath('.//text()')) for s in x],
                        lambda x: '; '.join([re.sub(r'\s+', ' ', s.replace('\n', '').strip()) for s in x]))
            i.add_xpath('latitude', '//meta[@itemprop="latitude"]/@content', base.get_first)
            i.add_xpath('longitude', '//meta[@itemprop="latitude"]/@content', base.get_first)
            if i.as_dict()['street_address'] != "<MISSING>" and i.as_dict()['location_name'] not in crawled:
                crawled.add(i.as_dict()['location_name'])
                return i

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=True
                )
        return results

    def crawl(self):
        base_url = "https://www.coffeebean.com/sitemap.xml"
        response = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        sitemap = response.content
        urls = []
        for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            if "store/usa" in url:
                urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
