import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Scraper import Scrape


URL = "https://qualityplusnc.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.exceptions = {
            "5635 US Hwy. 64 E. Ramseur NC 27316": {
                'address': '5635 US Hwy. 64 E.',
                'city': 'Ramseur',
                'state': 'NC',
                'zip': '27316'
            },
            "8385 S. Highway 55 Willow Springs NC 27592": {
                "address": "8385 S. Highway 55",
                'city': 'Willow Springs',
                'state': 'NC',
                'zip': '27592'
            },
            "1102 E. Hwy 54 Durham NC 27713": {
                "address": "1102 E. Hwy 54",
                'city': 'Durham',
                'state': 'NC',
                'zip': '27713'
            },
            "3162 NC Hwy 127 SE Hickory NC 28602": {
                "address": "3162 NC Hwy 127 SE",
                'city': 'Hickory',
                'state': 'NC',
                'zip': '28602'
            },
            "4050 US Hwy. 264 W. Washington NC 27889": {
                "address": "4050 US Hwy. 264 W.",
                'city': 'Washington',
                'state': 'NC',
                'zip': '27889'
            },
            "3086 N. Hwy. 221 Marion NC 28752": {
                "address": "3086 N. Hwy. 221",
                'city': 'Marion',
                'state': 'NC',
                'zip': '28752'
            },
            "5058 S. Main St. Shallotte NC 28470": {
                "address": "5058 S. Main St.",
                'city': 'Shallotte',
                'state': 'NC',
                'zip': '28470'
            },
            "202 North Queen Street, Elizabethtown NC 28337": {
                "address": "202 North Queen Street",
                'city': 'Elizabethtown',
                'state': 'NC',
                'zip': '28337'
            },
            "15531 US Hwy 17 N Hampstead NC 28443": {
                "address": "15531 US Hwy 17 N",
                'city': 'Hampstead',
                'state': 'NC',
                'zip': '28443'
            }
        }

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
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores
        location_url = "https://qualityplusnc.com/locations/"
        driver.get(location_url)
        stores = [data.get_attribute('innerHTML') for data in driver.find_elements_by_css_selector('script') if data.get_attribute('type') == 'text/javascript' and 'wpgmaps_localize' in data.get_attribute('innerHTML')][0]
        stores = json.loads([data for data in stores.split('\n') if 'wpgmaps_localize_marker_data' in data][0].replace('var wpgmaps_localize_marker_data = ', '')[:-1])['6']

        for id in stores.keys():
            store = stores[id]

            # Store ID
            location_id = store['marker_id']

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = 'Convenience Store'

            # Name
            location_title = store['title']

            # Street
            street_address = store['address'].split(',')[0] if store['address'] not in self.exceptions else self.exceptions[store['address']]['address']

            # city
            city = store['address'].split(',')[1] if store['address'] not in self.exceptions else self.exceptions[store['address']]['city']

            # zip
            zipcode = store['address'].split(',')[2][-5:] if store['address'] not in self.exceptions else self.exceptions[store['address']]['zip']

            # State
            state = store['address'].split(',')[2][:-5].strip() if store['address'] not in self.exceptions else self.exceptions[store['address']]['state']

            # Phone
            phone = store['desc'].split('</p>')[0].replace('<p>', '').split('<br />')[0]

            # Lat
            lat = store['lat']

            # Long
            lon = store['lng']

            # Hour
            hour = '24 Hour'

            # Country
            country = 'US'

            # Store data
            locations_ids.append(location_id)
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
            page_urls.append(page_url)

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
