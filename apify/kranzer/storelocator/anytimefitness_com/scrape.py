import asyncio
import re
from pprint import pprint
from string import capwords

import aiohttp
import base
import lxml.html
import requests, json
from urllib.parse import urljoin

import w3lib
from w3lib.html import remove_tags
from lxml import etree
crawled = set()
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = lxml.html.fromstring(resp)
            i = base.Item(sel)
            i.add_value('locator_domain', 'https://www.anytimefitness.com/find-gym/')
            i.add_value('page_url', url)
            js_ = sel.xpath('(//script[@type="application/ld+json"])[2]/text()')
            if js_:
                json_body = json.loads(js_[0])
                if not sel.xpath('//h2[contains(text(), "Coming")]') and 'coming' not in json_body['name'].strip().lower():
                    i.add_value('location_name', json_body['name'].strip())
                    i.add_value('phone', json_body['telephone'])
                    i.add_value('location_type', json_body['@type'])
                    i.add_value('street_address', json_body['address']['streetAddress'])
                    i.add_value('city', json_body['address']['addressLocality'])
                    i.add_value('state', json_body['address']['addressRegion'])
                    i.add_value('zip', json_body['address']['postalCode'])
                    i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
                    hours = sel.xpath('//ul[@class="staffed-hours-list"]')
                    hours_ = ' '.join(sel.xpath('//p[@class="hours"]/text()'))+'; '
                    if hours:
                        hours_ += w3lib.html.remove_tags(lxml.html.tostring(hours[0]).decode('utf8').replace('</li><li>', ', ').replace('</li></ul><li>', '; '))
                    if hours_[0] == ';':
                        hours_ = hours_[:1]
                    i.add_value('hours_of_operation', hours_)
                    i.add_xpath('latitude', '//div[@class="marker"]/@data-lat', base.get_first)
                    i.add_xpath('longitude', '//div[@class="marker"]/@data-lng', base.get_first)
                    if i.as_dict()['location_name'] not in crawled and i.as_dict()['country_code'] in {'US', 'CA'}:
                        crawled.add(i.as_dict()['location_name'])
                        if i.as_dict()['zip'] not in {'L76 0L5', 'V1C 358', 'V4V'}:
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
        base_urls = [
            'https://www.anytimefitness.com/gyms-sitemap1.xml',
            'https://www.anytimefitness.com/gyms-sitemap2.xml',
            'https://www.anytimefitness.com/gyms-sitemap3.xml',
            'https://www.anytimefitness.com/gyms-sitemap4.xml',
            'https://www.anytimefitness.com/gyms-sitemap5.xml',
            'https://www.anytimefitness.com/gyms-sitemap6.xml'
        ]
        urls = []
        for base_url in base_urls:
            response = requests.get(base_url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"})
            sitemap = response.content
            for sel in etree.fromstring(sitemap).xpath('//x:urlset/x:url/x:loc', namespaces={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}):
                url = sel.text
                if 'gyms/' in url:
                    urls.append(url)
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
