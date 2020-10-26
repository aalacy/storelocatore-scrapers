import asyncio
import re
import socket
from pprint import pprint
from string import capwords

import aiohttp
import base
import lxml.html
import sgrequests
from lxml import etree
crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        try:
            async with session.get(url, timeout=60 * 60, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36", "Connection": "close"}) as response:
                resp = await response.text()
                if resp:
                    sel = lxml.html.fromstring(resp)
                    i = base.Item(sel)
                    i.add_value('locator_domain', 'https://www.homedepot.com/l/storeDirectory')
                    i.add_value('page_url', url)
                    i.add_value('store_number', url.split('/')[-1])
                    i.add_xpath('location_name', '//h1[contains(@class, "storeName")]/text()', base.get_first)
                    i.add_xpath('phone', '//div[@class="storeDetailItem"]/span[@itemprop="telephone"]/text()', base.get_first)
                    i.add_xpath('street_address', '//div[contains(@class, "location_container_item")]/div/span[@itemprop="streetAddress"]/text()',
                                base.get_first, lambda x: x.strip())
                    i.add_xpath('city', '//div[contains(@class, "location_container_item")]/div/span/span[@itemprop="addressLocality"]/text()', base.get_first)
                    i.add_xpath('state', '//div[contains(@class, "location_container_item")]/div/span/span[@itemprop="addressRegion"]/text()', base.get_first)
                    i.add_xpath('zip', '//div[contains(@class, "location_container_item")]/div/span/span[@itemprop="postalCode"]/text()', base.get_first)
                    i.add_value('country_code', base.get_country_by_code(i.as_dict().get('state')))
                    i.add_xpath('hours_of_operation', '//li[@itemprop="openingHours"]/@content',
                                lambda x: '; '.join([s.replace('\xa0', ' ') for s in x]))
                    lat_lng = sel.xpath('//script/text()[contains(., "THD_GLOBAL")]')
                    if lat_lng:
                        store_type = re.findall(r'\{\"storeType\":\"(.+?)\"', lat_lng[0])
                        lat_lng_ = re.findall(r'\{\"lng\":(.+?),\"lat\":(.+?)\}', lat_lng[0])
                        try:
                            i.add_value('location_type', store_type[0])
                            i.add_value('latitude', lat_lng_[0][1])
                            i.add_value('longitude', lat_lng_[0][0])
                        except:
                            pass

                    if i.as_dict()['store_number'] not in crawled:
                        crawled.add(i.as_dict()['store_number'])
                        return i
        except:
            pass

    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=30, verify_ssl=False, family=socket.AF_INET)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return results

    def crawl(self):
        base_url = "https://www.homedepot.com/sitemap/d/store.xml"
        session = sgrequests.SgRequests()
        response = session.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36", "Connection": "close"})
        sitemap = response.content
        urls = []
        for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
            url = sel.text
            if not url.endswith('locations/'):
                urls.append(url)
        urls.append('https://www.homedepot.com/c/designcenter')
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
