from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.goldencorral.com/"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        driver.get("https://www.goldencorral.com/all-locations/")
        store_links = [link.get_attribute('href') for link in driver.find_elements_by_css_selector('div.all-locations-item > a.primary-link')]

        for store_link in store_links:
            print(f'Getting info for store {store_link}')
            driver.get(store_link)

            # Store ID
            location_id = store_link.replace('https://', '').strip('/').split('/')[2]

            # Page url
            page_url = store_link

            # Type
            location_type = 'Restaurant'

            # Name
            location_title = driver.find_element_by_css_selector('h1.heading-m').get_attribute('textContent')

            # Street
            street_address = ' '.join(driver.find_element_by_css_selector('div.location-detail-info-container > address').get_attribute('innerHTML').split('<br>')[:-1])

            # city
            city = driver.find_element_by_css_selector('div.location-detail-info-container > address').get_attribute('innerHTML').split('<br>')[1].split(',')[0]

            # zip
            zipcode = driver.find_element_by_css_selector('div.location-detail-info-container > address').get_attribute('innerHTML').split('<br>')[1].split(',')[1][-5:]

            # State
            state = driver.find_element_by_css_selector('div.location-detail-info-container > address').get_attribute('innerHTML').split('<br>')[1].split(',')[1][:-5].strip()

            # Phone
            phone = driver.find_element_by_css_selector('a.tel').get_attribute('textContent')

            # Lat
            lat = driver.find_element_by_css_selector('div.location-detail-info-container > address').get_attribute('data-lat')

            # Long
            lon = driver.find_element_by_css_selector('div.location-detail-info-container > address').get_attribute('data-lng')

            # Hour
            try:
                hour = driver.find_element_by_css_selector('ul.location-detail-hours').get_attribute('textContent')
            except:
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
