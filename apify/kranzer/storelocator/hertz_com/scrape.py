import asyncio
import aiohttp
import base

from w3lib.html import remove_tags

flatten = lambda l: [item for sublist in l for item in sublist]
crawled = set()
states_with_codes = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming',
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NT': 'Northwest Territories',
    'NS': 'Nova Scotia',
    'NU': 'Nunavut',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'QU': 'Quebec',
    'SK': 'Saskatchewan',
    'YT': 'Yukon'
}
class Scrape(base.Spider):
    async def _fetch_store(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            r = await response.json()
            if r:
                res = []
                for resp in r['data']['locations']:
                    i = base.Item(resp)

                    if not resp['extendedOAGCode']:
                        raise Exception("lol")
                    i.add_value('locator_domain', 'https://www.hertz.com/rentacar/location')
                    i.add_value('state', resp['stateProvinceCode'])
                    i.add_value('page_url', url
                                .replace('apiprod.', '')
                                .replace('country/CA', 'canada')
                                .replace('country/US', 'unitedstates')
                                .replace('rest', 'rentacar')
                                .replace(i.as_dict()['state'], states_with_codes[i.as_dict()['state']].lower().replace(' ',''))
                                .replace('state/', '')
                                .replace('city/', '')+'/'+resp['extendedOAGCode'])
                    i.add_value('city', resp['city'])
                    i.add_value('location_name', resp['locationName'])
                    i.add_value('country_code', resp['countryCode'])
                    i.add_value('zip', resp['zip'].strip(), lambda x: x+'3' if x == "2530" else x)
                    i.add_value('hours_of_operation', resp['hours'], remove_tags)
                    i.add_value('phone', resp['phoneNumber'].strip())
                    i.add_value('store_number', resp['extendedOAGCode'])
                    i.add_value('latitude', resp['latitude'])
                    i.add_value('longitude', resp['longitude'])
                    i.add_value('location_type', resp['type'], lambda x: "Corporate" if x == "C" else "Independent License")
                    i.add_value('street_address', ''.join([s for s in [resp['streetAddressLine1'], resp['streetAddressLine2']] if s.strip()]), remove_tags)

                    if i.as_dict()['store_number'] not in crawled:
                        crawled.add(i.as_dict()['store_number'])
                        res.append(i)
                return res

    async def _fetch_cities(self, session, urls):
        results = []
        for url in urls:
            res = await self._fetch_store(session, url)
            if res:
                results+=res
        return results

    async def _fetch_state(self, session, url):
        async with session.get(url, timeout=60 * 60) as response:
            resp = await response.json()
            city_names = [s['name'] for s in resp.get('data', {}).get('model', [])]
            cities_urls = [url.replace('geography/city/','location/')+'city/{}'.format(c) for c in city_names]
            cities = await self._fetch_cities(session, cities_urls)
            return cities


    async def _fetch_stores(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(loop=loop, connector=connector, headers={
            "Connection":"Keep-alive",
            "accept":"application/json",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"
        }) as session:
            results = await asyncio.gather(
                    *[self._fetch_state(session, url) for url in urls],
                    return_exceptions=False
                )
        return flatten(results)

    def crawl(self):
        urls = ["https://apiprod.hertz.com/rest/geography/city/country/US/state/{}/".format(s) for s in base.us_states_codes]
        urls += ["https://apiprod.hertz.com/rest/geography/city/country/CA/state/{}/".format(s) for s in list(base.ca_provinces_codes)+['QU']]
        loop = asyncio.get_event_loop()
        stores = loop.run_until_complete(self._fetch_stores(urls, loop))
        return [s for s in stores if s]



if __name__ == '__main__':
    s = Scrape()
    s.run()
