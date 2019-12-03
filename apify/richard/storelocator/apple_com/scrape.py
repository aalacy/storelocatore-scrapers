from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.apple.com/"


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
        page_urls = []
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        driver.get('https://www.apple.com/ca/retail/')
        stores = [url.get_attribute('value') for url in driver.find_elements_by_css_selector('div.select-style.select > select > option')[1:]]

        for store in stores:
            print(f'Getting result for {store}')
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            try:
                # Name
                location_title = driver.find_element_by_css_selector('h1.typography-section-headline').text
            except:
                location_title = '<MISSING>'

            # Page url
            page_url = store

            # Type
            location_type = 'Apple Store'

            try:
                # Street
                street_address = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(1)').text
            except:
                street_address = '<MISSING>'

            try:
                # city
                city = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[0]
            except:
                city = '<MISSING>'

            try:
                # zip
                zipcode = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][-7:]
            except:
                zipcode = '<MISSING>'

            try:
                # State
                state = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][:-7].strip()
            except:
                state = '<MISSING>'

            try:
                # Phone
                phone = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(4)').text
            except:
                phone = '<MISSING>'

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            try:
                # Hour
                hour = driver.find_element_by_css_selector('div.store-hours-container > div.store-hours').get_attribute('textContent').strip()
            except:
                hour = '<MISSING>'

            # Country
            country = 'Canada'

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

        driver.get("https://www.apple.com/retail/storelist/")
        stores = [url.get_attribute('href') for url in driver.find_element_by_css_selector('div.column.large-4.medium-12').find_elements_by_css_selector('a')]

        for store in stores:
            print(f'Getting result for {store}')
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            try:
                # Name
                location_title = driver.find_element_by_css_selector('h1.typography-section-headline').text
            except:
                location_title = '<MISSING>'

            # Page url
            page_url = store

            # Type
            location_type = 'Apple Store'

            try:
                # Street
                street_address = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(1)').text
            except:
                street_address = '<MISSING>'

            try:
                # city
                city = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[0]
            except:
                city = '<MISSING>'

            try:
                # zip
                zipcode = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][-5:]
            except:
                zipcode = '<MISSING>'

            try:
                # State
                state = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][:-5].strip()
            except:
                state = '<MISSING>'

            try:
                # Phone
                phone = driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(4)').text
            except:
                phone = '<MISSING>'

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            try:
                # Hour
                hour = driver.find_element_by_css_selector('div.store-hours').get_attribute('textContent')
            except:
                hour = '<MISSING>'

            # Country
            country = 'US'

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
