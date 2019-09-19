import json
<<<<<<< HEAD
=======
import sgzip
>>>>>>> master

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


<<<<<<< HEAD
URL = "https://www.catrentalstore.com/"
=======
URL = "https://www.catrentalstore.com"
>>>>>>> master


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
<<<<<<< HEAD
=======
        self.seen = []
>>>>>>> master

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
<<<<<<< HEAD
        location_types = []
        stores = []
=======
        dealers = []
>>>>>>> master

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
<<<<<<< HEAD
        location_url = "https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&searchType=address&searchValue=USA&maxResults=50&productDivId=2%2C1%2C6&appId=GdeKAczdmNrGwdPo"
        driver.get(location_url)
        stores = json.loads(driver.find_element_by_css_selector("pre").text)

        for store in stores:
            # Store ID
            location_id = store["dealerId"]

            # Name
            location_title = store["dealerName"]

            # Type
            location_type = store["type"]

            # Street
            street_address = (
                store["siteAddress"] + " " + store["siteAddress1"]
            ).strip()

            # Country
            country = store["countryCode"]

            # State
            state = store["siteState"]

            # city
            city = store["siteCity"]

            # zip
            zipcode = store["sitePostal"]

            # Lat
            lat = store["latitude"]

            # Long
            lon = store["longitude"]

            # Phone
            phone = store["locationPhone"]

            # hour
            hour_dict = {}
            for key in store["stores"][0].keys():
                if "storeHours" in key:
                    hour_dict[key] = store["stores"][0][key]

            hour = " ".join([day + " " + hour for day, hour in hour_dict.items()])

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
=======
        for zip_search in sgzip.for_radius(50):
            location_url = f"https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&searchType=address&searchValue={zip_search}&maxResults=50&productDivId=2%2C1%2C6&appId=GdeKAczdmNrGwdPo"
            driver.get(location_url)
            dealers.extend(json.loads(driver.find_element_by_css_selector("pre").text))

        for dealer in dealers:
            if dealer["dealerId"] not in self.seen:
                # Store ID
                location_id = dealer["dealerId"]

                # Name
                location_title = dealer["dealerName"]

                # Street
                street_address = (
                        dealer["siteAddress"] + " " + dealer["siteAddress1"]
                ).strip()

                # Country
                country = dealer["countryCode"]

                # State
                state = dealer["siteState"]

                # city
                city = dealer["siteCity"]

                # zip
                zipcode = dealer["sitePostal"]

                # Lat
                lat = dealer["latitude"]

                # Long
                lon = dealer["longitude"]

                # Phone
                phone = dealer["locationPhone"]

                # hour
                hour_dict = {}
                dealer_info = dealer["stores"][0]
                for key in dealer_info.keys():
                    if "storeHours" in key:
                        hour_dict[key] = dealer_info[key]
                hour = " ".join(
                    [day + " " + hour + "\n" for day, hour in hour_dict.items()]
                )

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
                self.seen.append(location_id)

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
>>>>>>> master
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
<<<<<<< HEAD
            location_types,
=======
>>>>>>> master
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
<<<<<<< HEAD
                    location_type,
=======
                    "<MISSING>",
>>>>>>> master
                    latitude,
                    longitude,
                    hour,
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
