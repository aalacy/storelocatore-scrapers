from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.mightypilates.com/"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        driver.get('https://www.mightypilates.com/locations/')
        stores = [store.find_element_by_css_selector('div.mk-text-block') for store in driver.find_elements_by_css_selector('div.mk-half-layout-container.page-section-content')]

        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Page url
            page_url = store.find_element_by_css_selector('h2').find_element_by_css_selector('a').get_attribute('href')

            # Type
            location_type = 'Pilates'

            # Street
            street_address = store.find_element_by_css_selector('p:nth-of-type(2)').get_attribute('innerHTML').split('<br>')[0]

            # city
            city = store.find_element_by_css_selector('p:nth-of-type(2)').get_attribute('innerHTML').split('<br>')[1].split(',')[0]

            # Name
            location_title = store.find_element_by_css_selector('h2').get_attribute('textContent')

            # zip
            zipcode = store.find_element_by_css_selector('p:nth-of-type(2)').get_attribute('innerHTML').split('<br>')[1].split(',')[1][-5:]

            # State
            state = store.find_element_by_css_selector('p:nth-of-type(2)').get_attribute('innerHTML').split('<br>')[1].split(',')[1][:-5].strip()

            # Phone
            phone = store.find_element_by_css_selector('p:nth-of-type(2)').get_attribute('innerHTML').split('<br>')[2].split('|')[0]

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Hour
            hour = '<MISSING>'

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
                    self.url.strip(),
                    page_url.strip(),
                    locations_title.strip(),
                    street_address.strip(),
                    city.strip(),
                    state.strip(),
                    zipcode.strip(),
                    country.strip(),
                    location_id.strip(),
                    phone_number.strip(),
                    location_type.strip(),
                    latitude.strip(),
                    longitude.strip(),
                    hour.strip(),
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
