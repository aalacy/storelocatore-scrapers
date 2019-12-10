import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.finishline.com/"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        for zip_search in sgzip.for_radius(50):
            driver.get(f"https://stores.finishline.com/search.html?q={zip_search}")
            data = [loc for loc in driver.find_elements_by_css_selector('li.location-list-result > article.location-card')]
            stores.extend(data)
            print(f"{len(data)} locations scraped for {zip_search}")

        for store in stores:
            if store.find_element_by_css_selector('h2.location-card-title').get_attribute('textContent').strip() not in self.seen:
                # Store ID
                location_id = '<MISSING>'

                # Name
                location_title = store.find_element_by_css_selector('h2.location-card-title').get_attribute('textContent').strip()

                # Page url
                page_url = '<MISSING>'

                # Type
                location_type = 'Retail'

                # Street
                street_address = store.find_element_by_css_selector('span.c-address-street-1').text

                # city
                city = store.find_element_by_css_selector('span.c-address-city > span').text

                # zip
                zipcode = store.find_element_by_css_selector('span.c-address-postal-code').text.strip()

                # State
                state = store.find_element_by_css_selector('abbr.c-address-state').text

                # Phone
                phone = store.find_element_by_css_selector('span.c-phone-number-span').text

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Hour
                hour = '<MISSING>'

                # Country
                country = store.find_element_by_css_selector('abbr.c-address-country-name').get_attribute('textContent')

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
                self.seen.append(location_title)

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
