import asyncio
import aiohttp
import base
from lxml import html
import sgrequests, json
from urllib.parse import urljoin

def check_sun(x):
    for s in x:
        if "sun " in s.lower():
            return True
    return False

class Scrape(base.Spider):

    async def _fetch_store(self, session, url):
        try:
            async with session.get(url, timeout=60 * 60) as response:
                resp = await response.text()
                res_sel = html.fromstring(resp)
                result = json.loads(res_sel.xpath('//div[@class="js-locator-item"]/script/text()')[0])
                i = base.Item(result)
                i.add_value('locator_domain', "https://www.freseniuskidneycare.com/dialysis-centers")
                i.add_value('page_url', url)
                i.add_value('location_name', result.get('name', '').strip())
                i.add_value('street_address', result.get('address', {}).get('streetAddress', '').strip())
                i.add_value('store_number', url.split('/')[-1])
                i.add_value('city', result.get('address', {}).get('addressLocality', '').strip())
                i.add_value('state', result.get('address', {}).get('addressRegion', '').strip(), base.get_state_code)
                i.add_value('zip', result.get('address', {}).get('postalCode', ''))
                i.add_value('phone', result.get('telephone', '').strip())
                i.add_value('country_code', i.as_dict()['state'], base.get_country_by_code)
                i.add_value('latitude', result.get('geo', {}).get('latitude', ''))
                i.add_value('longitude', result.get('geo', {}).get('longitude', ''))
                i.add_value('hours_of_operation', result.get('openingHours', []), lambda x: x+['Sun Closed'] if not check_sun(x) else x, lambda x: '; '.join(x))
                i.add_value('location_type', ', '.join(res_sel.xpath('//ul[preceding-sibling::h3[1][contains(text(), "Services")]]/li/a/text()')))
                return i
        except:
            return None


    async def _fetch_all_states(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(loop=loop, connector=connector, headers={
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }) as session:
            results = await asyncio.gather(
                    *[self._fetch_store(session, url) for url in urls],
                    return_exceptions=False
                )
        return results


    def crawl(self):
        stores = []
        base_url = "https://www.freseniuskidneycare.com/dialysis-centers?state={}"
        for state in base.us_states:
            session = sgrequests.SgRequests()
            body = html.fromstring(session.get(base_url.format(state.lower())).text)#.xpath('//div[@class="js-locator-item"]/script/text()')[0]
            locs = [urljoin(base_url, href) for href in body.xpath('//td[@class="locator-results-item-name"]/a[1]/@href')]
            loop = asyncio.get_event_loop()
            stores += loop.run_until_complete(self._fetch_all_states(locs, loop))

        return [s for s in stores if s]


if __name__ == '__main__':
    s = Scrape()
    s.run()
