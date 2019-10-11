import json
import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.audiusa.com"


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
        dealers = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        for zip_search in sgzip.for_radius(50):
            location_url = f"https://www.audiusa.com/vtp-service/search/dealers?zipcode={zip_search}&number=10000"
            driver.get(location_url)
            if 'dealers' in json.loads(driver.find_element_by_css_selector('pre').text).keys():
                dealers.extend(json.loads(driver.find_element_by_css_selector('pre').text)['dealers'])

        for dealer in dealers:
            if dealer['id'] not in self.seen:
                driver.get('https://' + dealer['website'] + '/dealership/about.htm')

                # Store ID
                location_id = dealer['id']

                # Name
                location_title = dealer['name']

                # Phone
                phone = dealer['phoneMobile'] if 'phoneMobile' in dealer.keys() else '<MISSING>'

                # Address
                street_address = dealer['street']

                # Hour
                try:
                    hour = driver.find_element_by_css_selector('div.hours-default.ddc-content.ddc-box-1.h-100').get_attribute('textContent')
                except:
                    hour = '<MISSING>'

                # Country
                country = 'US'

                # State
                state = dealer['state']

                # city
                city = dealer['city']

                # zip
                zipcode = dealer['zipCode']

                # Lat
                lat = dealer['position']['latitude']

                # Long
                lon = dealer['position']['longitude']

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
                self.seen.append(location_id)

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
