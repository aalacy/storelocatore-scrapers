import json
from pypostalcode import PostalCodeDatabase

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "scotiabank.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.stores_url = []
        self.provinces = []
        self.coords = []
        self.seen = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_type = []
        locations_titles = []
        street_addresses = []
        cities = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        stores = []
        countries = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        pcdb = PostalCodeDatabase()
        search = 'T3Z'
        radius = 3000
        self.coords.extend([(r.latitude, r.longitude) for r in pcdb.get_postalcodes_around_radius(search, radius)])

        for coord in self.coords:
            driver.get(f'https://mapsms.scotiabank.com/branches?1=1&latitude={coord[0]}&longitude={coord[1]}&recordlimit=20')
            try:
                stores = json.loads(driver.find_element_by_css_selector('body').get_attribute('innerHTML').replace('<br \="">', ''))['branchInfo']['marker']
                for store in stores:
                    if store['@attributes']['id'] not in self.seen:
                        # Location id
                        location_id = store['@attributes']['id']

                        # Location title
                        locations_title = store['name']

                        # Location type
                        location_type = '<MISSING>'

                        # Street address
                        street_address = store['address'].split(',')[-4]

                        # City
                        city = store['address'].split(',')[-3]

                        # State
                        state = store['address'].split(',')[-2]

                        # Zip code
                        zip_code = store['address'].split(',')[-1]

                        # Country
                        country = 'CA'

                        # Store hour
                        hour = store['hours']

                        # Phone
                        phone_number = store['phoneNo']

                        # Latitude
                        lat = store['@attributes']['lat']

                        # Longitude
                        lon = store['@attributes']['lng']

                        locations_ids.append(location_id)
                        locations_type.append(location_type)
                        locations_titles.append(locations_title)
                        street_addresses.append(street_address)
                        cities.append(city)
                        states.append(state)
                        zip_codes.append(zip_code)
                        phone_numbers.append(phone_number)
                        hours.append(hour)
                        countries.append(country)
                        latitude_list.append(lat)
                        longitude_list.append(lon)

                        self.seen.append(store['@attributes']['id'])
            except:
                pass


        for (
                locations_title,
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
                location_type
        ) in zip(
            locations_titles,
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
            locations_type
        ):
            self.data.append(
                [
                    self.url,
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

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
