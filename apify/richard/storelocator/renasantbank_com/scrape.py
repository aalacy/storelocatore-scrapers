import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.renasantbank.com/"


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

        # Fetch stores from location menu
        for num in range(1, 999):
            location_url = f"https://locations.renasantbank.com/wp-json/wp/v2/locations?per_page=100&page={num}"
            driver.get(location_url)
            result = json.loads(driver.find_element_by_css_selector("pre").text)
            if isinstance(result, list):
                stores.extend(result)
            else:
                break

        for store in stores:
            # Store ID
            location_id = store["id"] if store["id"] != "" else "<MISSING>"

            # Name
            location_title = (
                store["title"]["rendered"]
                if store["title"]["rendered"] != ""
                else "<MISSING>"
            )

            driver.get(store["link"])
            city_state_info = driver.find_element_by_css_selector(
                "div.hero-content.vert-center > div.wrapper > h2"
            ).get_attribute("textContent")

            # City
            city = city_state_info.split(",")[-2].strip()

            # State
            state = city_state_info.split(",")[-1].strip()[:2].upper()

            # Street Address
            street_address = " ".join(city_state_info.split(",")[:-2])

            # Zip
            zip_code = city_state_info.split(",")[-1].strip()[2:].strip()

            # Hours
            try:
                hour = driver.find_elements_by_css_selector('div.info-info')[1].get_attribute('textContent')
            except:
                hour = '<MISSING>'

            # Lat
            lat = (
                store["acf"]["latitude"]
                if "latitude" in store["acf"].keys() and store["acf"]["latitude"] != ''
                else "<MISSING>"
            )

            # Lon
            lon = (
                store["acf"]["longitude"]
                if "longitude" in store["acf"].keys() and store["acf"]["longitude"] != ''
                else "<MISSING>"
            )

            # Phone
            phone = (
                store["acf"]["phone_number"]
                if "phone_number" in store["acf"].keys() and "ATM" not in location_title and "ITM" not in location_title
                else "<MISSING>"
            ) if store["acf"]["phone_number"] != '' else '<MISSING>'

            # Country
            country = "US"

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
            if locations_title != "Jackson":
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
