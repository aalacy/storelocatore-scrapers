import requests
import json
import sgzip

from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('foodlion_com')



URL = "https://www.foodlion.com/"


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

        cookies = {
            'ApplicationGatewayAffinity': '57301a2606756ddb086aab8bfdbd554a',
            'userCountryCode': 'US',
            'gig_bootstrap_3_UoPaW48GjoIEQA-bkrH8ymLLtpVgtrAjwnUZYjgKAU1tEL48qefotwm0zjRKYRza': 'ver2',
            '_ga': 'GA1.2.170935166.1573882175',
            '_gcl_au': '1.1.1809662216.1573882176',
            '__utmzz': 'utmcsr=(direct)|utmcmd=(none)|utmccn=(not set)',
            '__utmzzses': '1',
            '_fbp': 'fb.1.1573882176636.1424744212',
            '__gads': 'ID=1c8fe9e1f38404b0:T=1573882176:S=ALNI_MZ_hSMDanMwziFDgZ8eEAvHHL9S9w',
            'userRegionCode': 'CA',
            'monthlyVisitPopUp': 'false',
            'userCity': 'FREMONT',
            'userCounty': 'ALAMEDA',
            'userZip': '94536-94539+94555',
            'userLat': '37.5710',
            'userLong': '-121.9858',
            '_gid': 'GA1.2.785592302.1576002304',
            '_gat_UA-1002630-3': '1',
            'JSESSIONID': 'node01j1n2b3tl368s41bksbletvx9449311.node0',
            '_derived_epik': 'dj0yJnU9TFpJRHJteUZsNHUydkV0U3VQRXRpU2h5cWNrOGRrWDAmbj1YejdkYnlVN1Z5NTJ6MEtSdy1IcFBBJm09NyZ0PUFBQUFBRjN2NHdR',
        }

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://www.foodlion.com/stores/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        # for coord_search in sgzip.coords_for_radius(50):
        for zipsearch in sgzip.for_radius(50):
            params = (
                ('zip', zipsearch),
                # ('lat', coord_search[0]),
                # ('lng', coord_search[1]),
                ('distance', '100'),
                ('onlyPharmacyEnabledStores', 'false'),
            )
            data = json.loads(requests.get('https://www.foodlion.com/bin/foodlion/search/storelocator.json', headers=headers, params=params).json()['result'])
            stores.extend(data)
            logger.info(f"{len(data)} locations scraped for {zipsearch}.")

        for store in stores:
            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Name
                location_title = store['title']

                # Page url
                page_url = store['href']

                # Type
                location_type = 'Grocery Store'

                # Street
                street_address = store['address']

                # city
                city = store['city']

                # zip
                zipcode = store['zip']

                # State
                state = store['state']

                # Phone
                phone = store['phoneNumber']

                # Lat
                lat = store['lat']

                # Long
                lon = store['lon']

                # Hour
                hour = ' '.join(store['hours'])

                # Country
                country = 'USA'

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
