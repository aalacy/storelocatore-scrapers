from demjson import decode
from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.mygym.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []

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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://www.mygym.com/locations'
        driver.get(location_url)
        stores = [link.get_attribute('outerHTML') for link in driver.find_elements_by_css_selector('script') if link.get_attribute('type') == 'text/javascript' and link.get_attribute('language') == 'javascript']
        stores = decode(stores[0].replace(';</script>', '').replace('<script type="text/javascript" language="javascript">', '').replace('var markers =', '').strip())

        for store in stores[1:]:
            if 'coming soon' not in store['addrdisplay'].lower() and store['country'] in ['United States', 'Canada']:
                # Store ID
                location_id = store['placeid']

                # Type
                location_type = 'Gym'

                # Name
                location_title = store['name']

                # Street
                street_address = ' '.join(store['addrdisplay'].strip('<br>').strip().split('<br>')[:-2])

                # city
                city = store['city']

                # zip
                zipcode = store['addrmap'][-5:]

                # State
                state = store['state']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Phone
                phone = store['phone']

                # Hour
                hour = '<MISSING>'

                # Country
                country = store['country']

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
                location_type,
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
            location_types,
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