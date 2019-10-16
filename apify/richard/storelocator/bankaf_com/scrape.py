import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://bankaf.com"


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
        stores = []
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        driver.get('https://bankaf.com/home/locations.html')
        coords = driver.find_element_by_css_selector('body > main > script').get_attribute('outerHTML')

        latitude = re.findall('lat: "(.+)",', coords)
        longitude = re.findall('lng: "(.+)",', coords)

        location_url = 'https://bankaf.com/home/locations.html'
        driver.get(location_url)
        stores.extend(driver.find_elements_by_css_selector('div.locations-pane'))

        counter = 0

        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = store.find_element_by_css_selector('span.locations-pane-header').text

            # Street Address
            street_address = store.find_element_by_css_selector('p.location-pane-contact-info > em:nth-of-type(1)').text

            # City
            city = store.find_element_by_css_selector('p.location-pane-contact-info > em:nth-of-type(2)').text.split(',')[0].strip()

            # State
            state = store.find_element_by_css_selector('p.location-pane-contact-info > em:nth-of-type(2)').text.split(',')[1].strip()[:-5].strip()

            # Zip
            zip_code = store.find_element_by_css_selector('p.location-pane-contact-info > em:nth-of-type(2)').text.split(',')[1].strip()[-5:].strip()

            # Hours
            hour = re.search('(?<=Hours).*', store.find_element_by_css_selector('p.location-pane-contact-info').get_attribute('textContent')).group().replace(':', '').replace(' of Operation', '').strip()

            # Lat
            lat = latitude[counter]

            # Lon
            lon = longitude[counter]

            # Phone
            phone = store.find_element_by_css_selector('p.location-pane-contact-info > span:nth-of-type(1) > a').text

            # Country
            country = 'US'

            # Store data
            locations_ids.append(location_id)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zip_code)
            hours.append(hour)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)
            counter += 1

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
