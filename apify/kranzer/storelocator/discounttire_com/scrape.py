import asyncio
import re
from pprint import pprint
from string import capwords

import aiohttp
import base
import lxml.html
import sgrequests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import etree
crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        async with session.get(url, allow_redirects=False,timeout=60 * 60, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}) as response:
            resp = await response.text()
            if resp:
                sel = lxml.html.fromstring(resp)
                i = base.Item(sel)
                i.add_value('locator_domain', 'https://www.discounttire.com/store-locator')
                i.add_value('page_url', url)
                i.add_value('store_number', url.split('/')[-1])
                addr = sel.xpath('//div[contains(@class, "store-quick-view__address")]/text()')
                if addr:
                    _ = [capwords(s) for s in addr[0].split(', ')]
                    i.add_value('street_address', _[0])
                    counter = 1
                    if base.get_state_code(_[counter]) == "<MISSING>":
                        counter+=1
                    i.add_value('state', base.get_state_code(_[counter]))

                    i.add_value('country_code', i.as_dict()['state'], base.get_country_by_code)
                    i.add_value('city', _[counter+1])
                    i.add_value('zip', _[counter+2])
                js = json.loads(sel.xpath('//script[@type="application/ld+json"][contains(text(), "openingHours")]/text()')[0])
                i.add_value('location_name', js['name'])
                i.add_value('phone', js['telephone'])
                i.add_value('hours_of_operation', '; '.join(js['openingHours']))
                # try:
                #     lat_lng = sel.xpath('//div[@class="static-map__container___1pH0L"][1]/@style')[0].split('=')[1]
                #     lat_lng = lat_lng[:lat_lng.find('&')]
                #     i.add_value('latitude', lat_lng.split(',')[0])
                #     i.add_value('longitude', lat_lng.split(',')[1])
                # except:
                #     pass
                i.add_value('latitude', "<INACCESSIBLE>")
                i.add_value('longitude', "<INACCESSIBLE>")
                if i.as_dict()['store_number'] not in crawled:
                    crawled.add(i.as_dict()['store_number'])
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
        base_url = "https://www.discounttire.com/medias/20191217-Discount-Tire-sitemap-categories.xml?context=bWFzdGVyfHJvb3R8NDU3ODM2fHRleHQveG1sfHN5cy1tYXN0ZXIvcm9vdC9oMzcvaDRiLzkxOTc5OTYxNDY3MTgvMjAxOTEyMTcgRGlzY291bnQgVGlyZSBzaXRlbWFwLWNhdGVnb3JpZXMueG1sfGM1MjVkODI3NmY3ODg2MjkzZmVjYzJkNTIzMWQ0ZTQxYzg1MDVhZDY4ZTQ3Y2Y2YWY0MmFiMmI3NTY0MGEzNzI"
        session = sgrequests.SgRequests()
        response = session.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
        sitemap = response.content
        urls = []
        for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            if "store/" in url:
                urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
