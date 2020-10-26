import json
import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.michaelkors.com/"


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
        page_urls = []
        countries = []
        stores = []
        location_types = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        for zip_search in sgzip.for_radius(100):
            location_url = f'https://locations.michaelkors.com/search.html?q={zip_search}&radius=100'
            driver.get(location_url)
            try:
                data = json.loads(driver.find_element_by_id('js-map-config-dir-map-desktop-map').get_attribute('textContent'))['locs']
            except:
                data = []
            stores.extend(data)
            print(f"{len(data)} locations received for zipcode: {zip_search}")

        for store in stores:
            if store['url'] not in self.seen and store['url'].split('/')[0] in ['us', 'ca']:
                url = "https://locations.michaelkors.com/" + store['url']
                driver.get(url)
                print(f"Getting data for {url}")

                # Location ID
                location_id = store['id']

                # Location name
                location_title = store['altTagText']

                # Page url
                page_url = url

                # Location type
                location_type = 'Retail'

                # Street address
                try:
                    street_address = driver.find_element_by_css_selector('span.c-address-street-1').get_attribute('textContent') + ' ' + driver.find_element_by_css_selector('span.c-address-street-2').get_attribute('textContent')
                except:
                    street_address = driver.find_element_by_css_selector('span.c-address-street-1').get_attribute('textContent')

                # City
                city = driver.find_element_by_css_selector('span.c-address-city').get_attribute('textContent')

                # State
                state = driver.find_element_by_css_selector('abbr.c-address-state').get_attribute('textContent')

                # Zip code
                zipcode = driver.find_element_by_css_selector('span.c-address-postal-code').get_attribute('textContent')

                # Phone
                phone = driver.find_element_by_css_selector('span.c-phone-number-span.c-phone-main-number-span').get_attribute('textContent')

                # Country
                country = 'US'

                # Latitude
                lat = store['latitude']

                # Longitude
                lon = store['longitude']

                # Hour
                try:
                    hour = driver.find_element_by_css_selector('table.c-location-hours-details > tbody').get_attribute('textContent')
                except:
                    hour = '<MISSING>'

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
                self.seen.append(store['url'])


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

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
