import asyncio
import aiohttp
import base
from lxml import html
import sgrequests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
crawled = set()
flatten = lambda l: [item for sublist in l for item in sublist]
base_url = "https://www.budget.com/en/locations/find-a-location"
headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        }

class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        if url.split('/')[-1] not in crawled:
            async with session.get(url, timeout=60 * 60, headers=headers) as response:
                resp = await response.text()
                res_sel = html.fromstring(resp)
                result = json.loads(res_sel.xpath('//script[@type="application/ld+json"]/text()')[0])
                i = base.Item(res_sel)
                i.add_value('locator_domain', "https://www.budget.com/en/locations/find-a-location")
                i.add_value('page_url', url)
                i.add_xpath('location_type', '//div[strong[contains(text(), "Location Type")]]/span/text()', base.get_first)
                i.add_xpath('location_name', '//div[@class="location-page-g"]/h2',
                            base.get_first,
                            lambda x: remove_tags(html.tostring(x))
                            .replace('\t','')
                            .replace('\n','')
                            .replace('\r','')
                            .replace('&#160;', ' ')
                            .strip())
                i.add_value('street_address', result.get('address', {}).get('streetAddress', '').strip())
                i.add_value('store_number', url.split('/')[-1])
                i.add_value('city', result.get('address', {}).get('addressLocality', '').strip())
                i.add_value('state', result.get('address', {}).get('addressRegion', '').strip(), lambda x: "Newfoundland and Labrador" if x == "Newfoundland" else x, base.get_state_code)
                i.add_value('zip', result.get('address', {}).get('postalCode', ''))
                i.add_value('phone', result.get('address', {}).get('telephone', '').strip(),
                            lambda x: x.split(' (')[0] if x.count(' ') == 2 else x,
                            lambda x: "<MISSING>" if x.strip()=="TBD" else x,
                            lambda x: x.split('/')[0] if '/' in x else x)
                i.add_value('country_code', i.as_dict()['state'], base.get_country_by_code)
                map = result.get('map')
                if map:
                    map = map.split('/')[-1].replace('?q=','').split(',')
                    i.add_value('latitude', map[0])
                    i.add_value('longitude', map[1])
                i.add_value('hours_of_operation', result.get('openingHours', ''))
                crawled.add(i.as_dict()['store_number'])
                return i

    async def _fetch_stores(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_store(session, url)
            if res:
                results.append(res)
        return results

    async def _fetch_state(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            sel = html.fromstring(resp)
            cities_urls = [urljoin(base_url, s) for s in sel.xpath('//ul[@class="location-list-ul"]/li[not(@class)]/a/@href')]
            cities = await self._fetch_stores(session, cities_urls)
            return cities

    async def _fetch_all_states(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=5)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_state(session, url) for url in urls],
                    return_exceptions=False
                )
        return flatten(results)


    def crawl(self):
        stores = []
        base_url = "https://www.budget.com/en/locations/find-a-location"
        session = sgrequests.SgRequests()
        body = html.fromstring(session.get(base_url).text)
        locs = [urljoin(base_url, href) for href in body.xpath('//div[contains(@class, "country-wrapper")]/ul/li/a/@href')]
        loop = asyncio.get_event_loop()
        stores += loop.run_until_complete(self._fetch_all_states(set(locs), loop))

        return [s for s in stores if s]


if __name__ == '__main__':
    s = Scrape()
    s.run()
