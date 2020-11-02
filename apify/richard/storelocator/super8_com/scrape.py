import re
import time

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('super8_com')




URL = "super8.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.stores_url = []
        self.provinces = []
        self.skip = [
            "https://www.wyndhamhotels.com/super-8/sawyer-michigan/super-8-sawyer-mi/overview"
        ]

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_type = []
        locations_titles = []
        street_addresses = []
        cities = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        stores = []
        countries = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        driver.get("https://www.wyndhamhotels.com/super-8/locations")
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


        stores.extend(
            [
                url.get_attribute("href")
                for url in driver.find_elements_by_css_selector("li.property > a:nth-of-type(1)")
            ]
        )

        for store in stores:
            if store not in self.skip and 'china' not in store and 'germany' not in store and 'saudi-arabia' not in store:
                logger.info(f"Now scraping: {store}")
                try:
                    driver.get(store)

                    # Wait until element appears - 10 secs max
                    wait = WebDriverWait(driver, 10)
                    wait.until(
                        ec.visibility_of_element_located(
                            (By.CSS_SELECTOR, ".uu-map-address.hidden-xs")
                        )
                    )

                    location_info = driver.find_element_by_css_selector(
                        "div.uu-map-address.hidden-xs > p"
                    ).text.split(",")

                    # Location id
                    location_id = "<MISSING>"

                    # Location title
                    locations_title = driver.find_element_by_css_selector(
                        "span.highlight-wrapper"
                    ).text

                    # Location type
                    location_type = "Hotel"

                    # Street address
                    street_address = ' '.join([detail.strip() for detail in location_info[0:-3]])

                    # City
                    city = location_info[-3].strip()

                    # State
                    state = location_info[-2].strip()

                    # Zip code
                    zip_code = location_info[-1].strip()

                    # Country
                    country = "US"

                    # Store hour
                    hour = "Always Open"

                    # Phone
                    phone_number = driver.find_element_by_css_selector(
                        "div.property-phone.hidden-xs > span > a"
                    ).text

                    if re.search(
                            "(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)",
                            driver.find_element_by_css_selector(
                                "div.directions-btn.action-btn.col-md-7.col-md-offset-8 > a"
                            ).get_attribute("href"),
                    ):
                        # Latitude
                        lat = (
                            re.search(
                                "(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)",
                                driver.find_element_by_css_selector(
                                    "div.directions-btn.action-btn.col-md-7.col-md-offset-8 > a"
                                ).get_attribute("href"),
                            )
                                .group()
                                .split(",")[0]
                        )

                        # Longitude
                        lon = (
                            re.search(
                                "(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)",
                                driver.find_element_by_css_selector(
                                    "div.directions-btn.action-btn.col-md-7.col-md-offset-8 > a"
                                ).get_attribute("href"),
                            )
                                .group()
                                .split(",")[1]
                        )
                    else:
                        lat = "<MISSING>"

                        lon = "<MISSING>"

                    locations_ids.append(location_id)
                    locations_type.append(location_type)
                    locations_titles.append(locations_title)
                    street_addresses.append(street_address)
                    cities.append(city)
                    states.append(state)
                    zip_codes.append(zip_code)
                    phone_numbers.append(phone_number)
                    hours.append(hour)
                    countries.append(country)
                    latitude_list.append(lat)
                    longitude_list.append(lon)
                except:
                    pass

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
            locations_type,
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
