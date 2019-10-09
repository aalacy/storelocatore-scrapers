from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.bmwmotorcycles.com"


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
        location_url = "https://c2b-services.bmw.com/c2b-localsearch/services/cache/v4/ShowAll?country=us&category=BD&clientid=UX_NICCE_FORM_DLO"
        driver.get(location_url)
        shops = []
        for num in range(1, 999):
            num = num * 5
            try:
                shop_info = driver.find_element_by_id(f"collapsible{num}")
                shops.append(shop_info)
            except:
                # Reached the end
                break

        for shop in shops:
            lines = shop.find_elements_by_css_selector(
                "div.collapsible-content > div.line > span.text"
            )

            # Store ID
            location_id = lines[12].get_attribute("textContent")

            # Name
            location_title = lines[1].get_attribute("textContent")

            # Country
            country = lines[2].get_attribute("textContent")

            # State
            state = lines[4].get_attribute("textContent")

            # city
            city = lines[5].get_attribute("textContent")

            # zip
            zipcode = lines[6].get_attribute("textContent")

            # Street
            street_address = lines[7].get_attribute("textContent")

            # Lat
            lat = lines[8].get_attribute("textContent")

            # Long
            lon = lines[9].get_attribute("textContent")

            # Phone
            phone = lines[16].get_attribute("textContent")

            # Store data
            locations_ids.append(location_id)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zipcode)
            hours.append("<MISSING>")
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
