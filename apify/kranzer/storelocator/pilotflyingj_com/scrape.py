import re
from string import capwords

import aiohttp
import base
import lxml
import requests, json
import asyncio
from urllib.parse import urljoin
from lxml import html
flatten = lambda l: [item for sublist in l for item in sublist]
class Scrape(base.Spider):


    async def _fetch_shop(self, session, url, result):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.text()
            i = base.Item(resp)
            i.add_value('locator_domain', "https://pilotflyingj.com/store-locations/")
            i.add_value('page_url', url)
            i.add_value('store_number', result['Id'])
            i.add_value('location_name', result['StoreName'])
            i.add_value('phone', result['PhoneNumber'])
            i.add_value('city', result['City'])
            i.add_value('street_address', result['StreetAddress'])
            i.add_value('state', result['State'])
            i.add_value('zip', result['ZipCode'])
            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']))
            coords_sel = lxml.html.fromstring(resp)
            coords = coords_sel.xpath('//li[span[contains(text(), "Coordinates")]]/text()')
            if coords:
                lat = coords[0].strip().split(' ')[0]
                lon = coords[0].strip().split(' ')[1]
                i.add_value('latitude', lat)
                i.add_value('longitude', lon)
            return i

    async def _fetch_all_states(self, profiles, loop):
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            results = await asyncio.gather(
                    *[self._fetch_shop(session, 'https://pilotflyingj.com/stores/{}/'.format(profile['Id']), profile) for profile in profiles],
                    return_exceptions=True
                )
        return results

    def crawl(self):
        base_url = 'https://pilotflyingj.com/umbraco/surface/storelocations/search'
        body = requests.post(base_url, headers={"Content-Type": "application/json"},data='{"PageNumber":1,"PageSize":10000000,"States":[],"Countries":[],"Concepts":[]}').json()
        profiles = body.get('Locations', [])
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_all_states(profiles, loop))
        return stores


if __name__ == '__main__':
    s = Scrape()
    s.run()
