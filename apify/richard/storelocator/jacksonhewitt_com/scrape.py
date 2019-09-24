import sgzip

import xmltodict
from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.jacksonhewitt.com"


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
        stores = []
        seen = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        for zip_search in sgzip.for_radius(50):
            location_url = f"https://www.jacksonhewitt.com/api/offices/search/{zip_search}"
            driver.get(location_url)

            for id in range(2, 9999, 9):
                try:
                    stores.extend(driver.find_element_by_id(f"collapsible{id}"))
                except:
                    # Reached the end
                    break

        for store in stores:
            if store_infos[0] not in seen:
                store_infos = store.find_elements_by_css_selector("span.text")
                store_infos = [
                    store_info.text for store_info in store_infos if store_info.text != ""
                ]

                # Store ID
                location_id = '<MISSING>'

                # Name
                location_title = "Hackson Hewitt" + " " + store_infos[1]

                # Type
                location_type = store_infos[-7]

                # Street
                street_address = store_infos[0]

                # Country
                country = "US"

                # State
                state = store_infos[-3]

                # city
                city = store_infos[-4]

                # zip
                zipcode = store_infos[-1]

                # Lat
                lat = store_infos[5]

                # Long
                lon = store_infos[8]

                # Phone
                phone = store_infos[-8]

                # hour
                hour_list = [hour for hour in store_infos[10:24]]
                hour = " ".join(hour_list)

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
                seen.append(store_infos[0])

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
