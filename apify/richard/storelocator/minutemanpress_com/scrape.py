import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.minutemanpress.com/"


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

        for search_country in ['us']:
            stores = []
            prov_state = 'provinces' if search_country == 'ca' else 'states'
            print(f"Getting {prov_state} for {search_country.upper()}")
            driver.get(f'https://www.minutemanpress.com/locations/locations.html/{search_country}')
            states = [url.get_attribute('action') for url in driver.find_elements_by_css_selector('div.mmp-corp-store-search-filter-options > form')]
            for state in states:
                print(f"Getting stores for state website: {state}")
                driver.get(state)
                stores.extend([store_url.get_attribute('href') for store_url in driver.find_elements_by_css_selector('a.visit-website.button')])

            print("\n Preparing for scrape each store. \n")

            for store in stores:
                print(f"Getting url for {store}")
                driver.get(store)

                try:
                    # Store ID
                    location_id = '<MISSING>'

                    # Page url
                    page_url = store

                    # Type
                    location_type = 'Print Center'

                    # Street
                    address_info = [re.sub('(Canada)|(United States)', '', address.get_attribute('textContent')).replace('\t', '').replace('\n', '').strip() for address in driver.find_element_by_css_selector('div.location__address').find_elements_by_css_selector('div') if address.get_attribute('itemprop') == 'streetAddress']
                    address_info = [info for info in address_info if info != '']
                    street_address = ' '.join(address_info[:-1])

                    # zip
                    zipcode = address_info[-1][-5:].strip() if search_country == 'us' else address_info[-1][-7:].strip()

                    # city
                    city = address_info[-1].replace(zipcode, '').split(',')[0].strip()

                    # Name
                    location_title = f"Minute man press - {city}"

                    # State
                    state = address_info[-1].replace(zipcode, '').split(',')[1].strip()

                    # Phone
                    phone = driver.find_element_by_css_selector('div.location-phone.location-phone--1 > span.value > a').get_attribute('textContent')

                    # Lat
                    lat = '<MISSING>'

                    # Long
                    lon = '<MISSING>'

                    # Hour
                    try:
                        hour = driver.find_element_by_css_selector('div.location__hours').get_attribute('textContent').replace('\n', '').replace('\t', '').strip()
                    except:
                        hour = '<MISSING>'

                    # Country
                    country = search_country.upper()

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
                except:
                    print(f"{store} is not scrapable")
                    pass

            print(f"Done scraping stores for {search_country.upper()}")

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
