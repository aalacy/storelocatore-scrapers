from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.menchies.com/"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://www.menchies.com/all-locations'
        driver.get(location_url)
        stores = [info for info in driver.find_elements_by_css_selector('div.state-wrapper > div.loc-info')]

        for store in stores:
            # Name
            location_title = store.find_element_by_css_selector('span.font-purple.title-case').get_attribute('textContent')

            print(f"Currently scraping: {location_title}")

            # Store ID
            location_id = '<MISSING>'

            # Type
            location_type = 'Frozen Yogurt Shop'

            # Name
            location_title = store.find_element_by_css_selector('span.font-purple.title-case').get_attribute('textContent')

            # Street
            street_address = ' '.join(store.find_element_by_css_selector('div.loc-address').get_attribute('innerHTML').split('<br>')[:-1])

            # city
            city = store.find_element_by_css_selector('div.loc-address').get_attribute('innerHTML').split('<br>')[-1].split(',')[0]

            # zip
            zipcode = store.find_element_by_css_selector('div.loc-address').get_attribute('innerHTML').split('<br>')[-1].split(',')[1][-5:]

            # State
            state = store.find_element_by_css_selector('div.loc-address').get_attribute('innerHTML').split('<br>')[-1].split(',')[1][:-5].strip()

            # Phone
            try:
                phone = store.find_element_by_css_selector('p.loc-phone').get_attribute('textContent')
            except:
                phone = '<MISSING>'

            # Lat
            try:
                lat = store.find_element_by_css_selector('p.loc-directions > a').get_attribute('href').replace('https://maps.google.com/?daddr=', '').split(',%')[0]
                lon = store.find_element_by_css_selector('p.loc-directions > a').get_attribute('href').replace('https://maps.google.com/?daddr=', '').split(',%')[1].strip('-20')
            except:
                lat = '<MISSING>'
                lon = '<MISSING>'

            # Hour
            hour = ' '.join([hour.get_attribute('textContent') for hour in store.find_elements_by_css_selector('p.loc-hours')])

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
            if 'COMING SOON' in locations_title:
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