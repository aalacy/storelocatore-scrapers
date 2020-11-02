import json
from pypostalcode import PostalCodeDatabase

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.chapters.indigo.ca/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []
        self.postal_codes = []

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
        search = 'S7H'
        radius = 3000
        self.postal_codes = [loc.postalcode + '0A0' for loc in pcdb.get_postalcodes_around_radius(search, radius)]

        for postal_search in self.postal_codes:
            location_url = f'https://www.chapters.indigo.ca/en-CA/api/v1/storeavailability/getstores?province=&cityPostal={postal_search}&null'
            driver.get(location_url)
            resp = json.loads(driver.find_element_by_css_selector('pre').text)
            stores.extend(resp['stores'] if 'stores' in resp.keys() else [])

        for store in stores:
            if store['ID'] not in self.seen:
                self.seen.append(store['ID'])

                # Location id
                location_id = store['ID']

                # Location title
                locations_title = store['Name']

                # Location type
                location_type = store['Type']

                # Street address
                street_address = store['Address']

                # City
                city = store['City']

                # State
                state = store['Province']

                # Country
                country = store['Country']

                # Zip code
                zip_code = store['PostalCode'].strip()

                # Store hour
                hour = store['HoursRow']

                # Phone
                phone_number = store['PhoneNum']

                # Latitude
                lat = store['Latitude']

                # Longitude
                lon = store['Longitude']

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
