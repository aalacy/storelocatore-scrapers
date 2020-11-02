import requests
import sgzip

from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kay_com')



URL = "https://www.kay.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_titles = []
        street_addresses = []
        cities = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        countries = []
        location_types = []
        page_urls = []
        stores = []

        headers = {
            'authority': 'www.kay.com',
            'accept': '*/*',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.kay.com/store-finder',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': 'JSESSIONID=708433FE2206166ABDDCC4CBE61173C3; ROUTEID=.node9; AKA_A2=A; akaalb_prod-kay=~op=prod_kay:prod2kay|~rv=96~m=prod2kay:0|~os=1f2f3e33771e07b3045bd0ccbe2c164e~id=bbf01fb21fc69c2cba5e4c40c422e602; AMCVS_700CFDC5570CBFE67F000101%40AdobeOrg=1; AMCV_700CFDC5570CBFE67F000101%40AdobeOrg=690614123%7CMCIDTS%7C18238%7CMCMID%7C55906249452249183694569090769834606863%7CMCAAMLH-1576365637%7C9%7CMCAAMB-1576365637%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1575768036s%7CNONE%7CMCAID%7C2E9C880705035FDF-40001195400002FE%7CvVersion%7C3.1.0; AMP_TOKEN=%24NOT_FOUND; ak_bmsc=59FD134210148F1E8C73D62D5075D051B81BB3A84A7E0000C333EC5D989CAE3C~plQQjmN2/0HUmdRpSMJKAEMijBLZpJ4tyhzyt4t/9YxVZyx5s3Nm2MYKaqlzDMoP2PpNKlkcw8B0+9dRjZQc1ynfF3+neIGq6z3JoPccAK5EMB5Xs33o07LPmUzVgPOXClhqblDvp3cCWN1aFuN6zt/bAyL7VzZKe+OCzYsvTFw6OYyhvjqTAmv8V2IVT5/WqP4fxgEA/0xHLNTRzsEWHTpm9EJRH5BpejX95qFdFTxIwR7DYaphJXYNu76ZwWMLCb; _ga=GA1.2.315703271.1575760838; _gid=GA1.2.638623448.1575760838; _gat=1; s_cc=true; _gcl_au=1.1.1187953478.1575760838; crl8.fpcuid=793b087e-17fa-4bbc-aa5c-364a78bbd4c6; _scid=25c60cc7-0817-4c37-a5bd-7035a2fbd715; kampyle_userid=5af1-60b1-40de-4ebc-904c-b101-73a1-f5c1; kampyleUserSession=1575760838331; kampyleUserSessionsCount=1; _mibhv=anon-1575760838360-4287413449_4964; _micpn=esp:-1::1575760838360; cd_user_id=16ee2aa3eeabd8-07c6a0e4464569-3964720e-13c680-16ee2aa3eebb40; dtm_token=AQEIvwTYibS-NgFczv_oAQHzYQE; _fbp=fb.1.1575760838568.160642754; _sctr=1|1575705600000; usi_return_visitor=Sat%20Dec%2007%202019%2015%3A20%3A39%20GMT-0800%20(Pacific%20Standard%20Time); usi_first_hit=1; usi_launched25500=t1575760848010; smtrrmkr=637113576693341536%5E016ee2aa-4070-471a-a568-9034a8b66dfe%5E016ee2aa-4070-4c86-b978-eca24b9e1827%5E0%5E199.201.64.137; _derived_epik=dj0yJnU9M0diNmVhNE5wd0h1bUNzQWx1TzZlNFpXT2VWd1hHWEUmbj05MWhwem1oTV9QRmd1dm55U190UVd3Jm09NyZ0PUFBQUFBRjNzTS1j; gpv_pn=kay%3AStore%20Locator%20Results; sailthru_pageviews=3; kampyleSessionPageCounter=4; akavpau_prod_kay_vp=1575761171~id=71e269cb3312a8cc2cb35443461822f9; bm_sv=B4C4C25086C071630DC07A39D894380B~SFHb1uCNIIRWfGoc8KOLw/bvHCS72/qR79V5diFwQ3KPns6lfnkYoljO6YSivZlHAZj32gF/NjRWDnZpLPtUewGYidYb8WmGkvDr5A8T6kbtWpl8eqBWdpjW977SKPmPmSjEek81qe3s04na0E6SDQ==; sailthru_content=27155c5e59bd574afa874002d2284a2885470429b5fc5c9dc3580af0de4585da; sailthru_visitor=fa448690-25c1-4e07-84a7-5f3cc6327a54; RT="sl=4&ss=1575760835004&tt=6377&obo=0&bcn=%2F%2F17d98a59.akstat.io%2F&sh=1575760871301%3D4%3A0%3A6377%2C1575760868890%3D3%3A0%3A5454%2C1575760854883%3D2%3A0%3A4533%2C1575760837931%3D1%3A0%3A2920&dm=kay.com&si=aa99fe9d-6dd2-4451-97a9-3605f78844b3&ld=1575760871301&nu=&cl=1575760875511"; s_gnr=1575760875513-New; s_sq=%5B%5BB%5D%5D',
        }

        for zip_search in sgzip.for_radius(50):
            pages = 999
            data = []
            for page in range(0, pages):
                params = (
                    ('q', zip_search),
                    ('page', page),
                    ('includeKayStores', 'true'),
                    ('includeKayOutletStores', 'true'),
                )

                res = requests.get('https://www.kay.com/store-finder/find', headers=headers, params=params).json()

                if res['total'] == '':
                    break

                data.extend(res['data'])
                if len(data) == res['total']:
                    stores.extend(data)
                    logger.info(f"{res['total']} stores scraped for zipcode {zip_search}")
                    break

        for store in stores:
            if store['name'] not in self.seen:
                # Store ID
                location_id = store['name']

                # Name
                location_title = store['displayName']

                # Page url
                page_url = store['url']

                # Type
                location_type = 'Retail'

                # Street
                street_address = (store['line1'] + ' ' + store['line2']).strip()

                # city
                city = store['town']

                # zip
                zipcode = store['postalCode']

                # State
                state = store['regionIsoCodeShort']

                # Phone
                phone = store['phone']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Hour
                hour = ' '.join([
                    f"{day} {hour}" for day, hour in store['openings'].items()
                ]) if 'openings' in store.keys() else '<MISSING>'

                # Country
                country = 'US'

                # Store data
                locations_ids.append(location_id)
                page_urls.append(page_url)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                states.append(state)
                zip_codes.append(zipcode)
                hours.append(hour)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                cities.append(city)
                countries.append(country)
                location_types.append(location_type)
                self.seen.append(location_id)

        for (
                locations_title,
                page_url,
                street_address,
                city,
                state,
                zipcode,
                phone_number,
                latitude,
                longitude,
                hour,
                location_id,
                country,
                location_type,
        ) in zip(
            locations_titles,
            page_urls,
            street_addresses,
            cities,
            states,
            zip_codes,
            phone_numbers,
            latitude_list,
            longitude_list,
            hours,
            locations_ids,
            countries,
            location_types,
        ):
            self.data.append(
                [
                    self.url,
                    page_url,
                    locations_title,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country,
                    location_id,
                    phone_number,
                    location_type,
                    latitude,
                    longitude,
                    hour,
                ]
            )


scrape = Scraper(URL)
scrape.scrape()
