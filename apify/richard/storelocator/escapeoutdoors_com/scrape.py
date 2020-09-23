from Scraper import Scrape
from sgselenium import SgSelenium
import time
import re

URL = "https://www.escapeoutdoors.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_urls = []
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

        driver = SgSelenium().chrome()
        time.sleep(2)

        location_url = 'https://www.escapeoutdoors.com/pages/find-a-store'
        driver.get(location_url)
        time.sleep(8)

        stores = driver.find_elements_by_css_selector('tbody')

        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = store.find_element_by_css_selector('p:nth-of-type(1)').text

            # Type
            location_type = '<MISSING>'

            # Street
            street_address = store.find_element_by_css_selector('p:nth-of-type(2)').text

            # State
            state = store.find_element_by_css_selector('p:nth-of-type(3)').text.split(',')[1].strip()[:-5].strip()

            # city
            city = store.find_element_by_css_selector('p:nth-of-type(3)').text.split(',')[0]

            # zip
            zipcode = store.find_element_by_css_selector('p:nth-of-type(3)').text.split(',')[1].strip()[-5:]

            map_link = store.find_element_by_tag_name("iframe").get_attribute("src")
            lat_pos = map_link.rfind("!3d")
            lat = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
            lng_pos = map_link.find("!2d")
            lon = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()

            # Phone
            phone = store.find_element_by_css_selector('p:nth-of-type(4)').text.replace('Phone:', '').strip()

            # Hour
            try:
                hour = store.find_element_by_css_selector('p:nth-of-type(7)').text + ' ' + store.find_element_by_css_selector('p:nth-of-type(8)').text + ' ' + store.find_element_by_css_selector('p:nth-of-type(9)').text
            except:
                hour = store.find_element_by_css_selector('p:nth-of-type(6)').text + ' ' + store.find_element_by_css_selector('p:nth-of-type(7)').text
            hour = (re.sub(' +', ' ', hour)).strip()

            # Country
            country = 'US'

            # Store data
            locations_ids.append(location_id)
            locations_urls.append(location_url)
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
                locations_url,
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
            locations_urls,
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
                        locations_url,
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
