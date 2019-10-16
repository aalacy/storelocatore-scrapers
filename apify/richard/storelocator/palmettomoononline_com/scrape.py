import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.palmettomoononline.com"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://client.lifterlocator.com/maps/jsonGet/palmettomoon.myshopify.com?storeName=palmettomoon.myshopify.com&mapId=786&loadSource=click&maxResults=10000&radius=25000&zoom=3&address=Atlanta%2C+GA+30346%2C+USA&latitude=33.9260395&longitude=-84.3410586&initialView=auto&measurement=mi&_=1569734034545'
        driver.get(location_url)
        stores = json.loads(driver.find_element_by_css_selector('pre').text)

        for store in stores:
            # Store ID
            location_id = store["id"]

            # Name
            location_title = store["title"]

            # Type
            location_type = '<MISSING>'

            # Street
            street_address = ' '.join(store["address"].split(',')[:-2])

            # State
            state = store["address"].split(',')[-1].strip()[:-5]

            # city
            city = store["address"].split(',')[-2].strip()

            # zip
            zipcode = store["address"].split(',')[-1].strip()[-5:]

            # Lat
            lat = store['lat']

            # Long
            lon = store['lng']

            # Phone
            phone = store["phone"]

            # Hour
            hour = store['description'].split('</i>')[-1].replace('<br/>', '')

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
            if country == "<MISSING>":
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
