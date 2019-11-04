from demjson import decode
from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://vapiano.com"


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

        location_url = 'https://us.vapiano.com/en/restaurants/'
        driver.get(location_url)
        stores = driver.find_element_by_css_selector('div.restaurant-wrapper > script').get_attribute('outerHTML').replace('<script>', '').strip().split('\n')[0].replace("var restaurants = '", '')[:-2]
        stores = decode(stores)

        for store in stores:
            if store['country'] in ['USA', 'Canada']:
                # Store ID
                location_id = store['storeId']

                # Type
                location_type = 'Restaurant'

                # Name
                location_title = store['address']

                # Street
                street_address = store['address2']

                # city
                city = store['city']

                # zip
                zipcode = store['zip'][-5:]

                # State
                state = store['zip'][:2]

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Phone
                phone = store['telephone']

                # Hour
                hour = ' '.join(store['opening'].split('<br />'))

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