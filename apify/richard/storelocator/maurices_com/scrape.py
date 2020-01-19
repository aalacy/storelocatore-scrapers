from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.maurices.com/"


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
        state_urls = []
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        country_urls = ['https://locations.maurices.com/ca', 'https://locations.maurices.com/us']

        for url in country_urls:
            print(f"Getting info for {url}")
            driver.get(url)
            state_data = [state_url.get_attribute('href') for state_url in driver.find_elements_by_css_selector('a.Directory-listLink')]
            state_urls.extend(state_data)

        for state_url in state_urls:
            print(f"Getting info for {state_url}")
            driver.get(state_url)
            stores.extend([city.get_attribute('href') for city in driver.find_elements_by_css_selector('a.Directory-listLink') if city.get_attribute('data-count') == '(1)'])
            multi_stores = [city.get_attribute('href') for city in driver.find_elements_by_css_selector('a.Directory-listLink') if city.get_attribute('data-count') != '(1)']
            for multi_store in multi_stores:
                driver.get(multi_store)
                stores_links = [link.get_attribute('href') for link in driver.find_elements_by_css_selector('div.Teaser-link.Teaser-cta > a') if link.get_attribute('textContent') == 'Store Details']
                stores.extend(stores_links)

        stores.extend(
            [
                'https://locations.maurices.com/us/md/lavale/1262-vocke-road',
                'https://locations.maurices.com/us/ri/lincoln/622-george-washington-highway',
                'https://locations.maurices.com/ca/pe/charlottetown/202-buchanan-drive'
            ]
        )

        for store in stores:
            print(f"Getting details for {store}")
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            # Name
            try:
                location_title = driver.find_element_by_id('location-name').get_attribute('textContent')
            except:
                location_title = driver.find_element_by_id('LocationName').get_attribute('textContent')

            # Page url
            page_url = store

            # Type
            location_type = 'Retail'

            # Street
            street_address = driver.find_element_by_css_selector('span.c-address-street-1').get_attribute('textContent')

            # city
            city = driver.find_element_by_css_selector('span.c-address-city').get_attribute('textContent')

            # zip
            zipcode = driver.find_element_by_css_selector('span.c-address-postal-code').get_attribute('textContent')

            # State
            state = driver.find_element_by_css_selector('abbr.c-address-state').get_attribute('textContent')

            # Phone
            phone = driver.find_element_by_id('phone-main').get_attribute('textContent')

            # Lat
            lat = driver.find_element_by_css_selector('span.coordinates > meta:nth-of-type(1)').get_attribute('content')

            # Long
            lon = driver.find_element_by_css_selector('span.coordinates > meta:nth-of-type(2)').get_attribute('content')

            # Hour
            hour = driver.find_element_by_css_selector('table.c-hours-details').get_attribute('textContent')

            # Country
            country = store.replace('https://', '').split('/')[1].upper()

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
