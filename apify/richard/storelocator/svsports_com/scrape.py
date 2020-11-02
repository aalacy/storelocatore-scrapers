import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('svsports_com')




URL = "https://www.svsports.com/"


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

        location_url = 'https://www.svsports.com/storelocator.cfm'
        driver.get(location_url)
        stores = [link.get_attribute('href') for link in driver.find_elements_by_css_selector('div.storeContainer > div.mapAddress > a:nth-of-type(2)')]

        for store in stores:
            if store != 'https://www.svsports.com/':
                logger.info(f'Scraping {store}')

                driver.get(store)

                address_info = driver.find_element_by_css_selector('div.containedContent > p:nth-of-type(2)').get_attribute('textContent').replace('Address: ', '').split(',')

                # Store ID
                location_id = '<MISSING>'

                # Type
                location_type = '<MISSING>'

                # Name
                location_title = driver.find_element_by_css_selector('div.page-heading').get_attribute('textContent')

                # Street
                street_address = address_info[0].strip()

                # city
                city = address_info[1].strip()

                # zip
                zipcode = address_info[2].strip().split(' ')[1]

                # State
                state = address_info[2].strip().split(' ')[0]

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Phone
                phone = driver.find_element_by_css_selector('div.containedContent > p:nth-of-type(3)').get_attribute('textContent').replace('Phone:', '').strip()

                # Hour
                hour = re.sub('(Get Directions).+', '', ' '.join([item.get_attribute('textContent') for item in driver.find_elements_by_css_selector('div.containedContent > p:nth-of-type(n+4)')]))

                # Country
                country = 'USA'

            else:
                address_info = driver.find_element_by_css_selector('div.containedContent > p:nth-of-type(2)').get_attribute('textContent').replace('Address: ', '').split(',')

                # Store ID
                location_id = '<MISSING>'

                # Type
                location_type = '<MISSING>'

                # Name
                location_title = "Schuylkill Valley Sports in Pottstown, PA"

                # Street
                street_address = "18 W Lightcap Rd Suite 1005"

                # city
                city = "Pottstown"

                # zip
                zipcode = "19464"

                # State
                state = "PA"

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Phone
                phone = "<MISSING>"

                # Hour
                hour = "<MISSING>"

                # Country
                country = 'USA'

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
            if country == "<MISSING>":
                pass
            else:
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
