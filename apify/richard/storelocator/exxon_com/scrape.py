import json
import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('exxon_com')




URL = "https://www.exxon.com/"


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
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        for coords in sgzip.coords_for_radius(50):
            lat1 = str(float(coords[0]) - 0.5)
            lat2 = str(float(coords[0]) + 0.5)
            lon1 = str(float(coords[1]) + 0.5)
            lon2 = str(float(coords[1]) - 0.5)
            location_url = f'https://www.exxon.com/en/api/v1/Retail/retailstation/GetStationsByBoundingBox?Latitude1={lat1}&Latitude2={lat2}&Longitude1={lon1}&Longitude2={lon2}'
            driver.get(location_url)
            try:
                data = json.loads(driver.find_element_by_css_selector('pre').text)
                logger.info(f'{len(data)} locations scraped')
                stores.extend(data)
            except:
                logger.info('0 locations scraped')
                pass

        for store in stores:
            if store['LocationID'] not in self.seen:
                # Store ID
                location_id = store['LocationID']

                # Name
                location_title = store['DisplayName']

                # Phone
                phone = store['Telephone']

                # Address
                street_address = store['AddressLine1'] + store['AddressLine2']

                # Hour
                hour = store['WeeklyOperatingDays']

                # Country
                country = store['Country']

                # State
                state = store['StateProvince']

                # city
                city = store['City']

                # zip
                zipcode = store['PostalCode']

                # Lat
                lat = store['Latitude']

                # Long
                lon = store['Longitude']

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
                self.seen.append(store['LocationID'])

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
                    "<MISSING>",
                    latitude,
                    longitude,
                    hour,
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
