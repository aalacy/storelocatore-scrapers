import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.chemungcanal.com"


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
        dealers_ll_dict = {}

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Lat/long
        driver.get('https://www.chemungcanal.com/modules/locations/library/gmap.php')
        dealers_ll = json.loads(driver.find_element_by_css_selector('pre').text)
        for dealer in dealers_ll:
            dealers_ll_dict[dealer['Name']] = [dealer['Lat'], dealer['Lng']]

        # Fetch stores from location menu
        location_url = "https://www.chemungcanal.com/locations/"
        driver.get(location_url)
        dealers = [dealer for dealer in driver.find_elements_by_css_selector('li.flexcol-xs-12.flexcol-sm-6.flexcol-md-4.flexcol-xl-4')]

        for dealer in dealers:
            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = dealer.find_element_by_css_selector('div.location-box.height-100 > h3').text

            # Phone
            phone = '<MISSING>' if 'ATM' in location_title else dealer.find_element_by_css_selector('div.location-box.height-100 > p').get_attribute('textContent')

            # Address
            street_address = dealer.find_element_by_css_selector('div.location-address > p').get_attribute('textContent').split('\n')[1]

            # Hour
            hour = '<MISSING>' if 'ATM' in location_title else dealer.find_element_by_css_selector('div.location-hours').get_attribute('textContent')

            # Country
            country = 'US'

            # State
            state = dealer.find_element_by_css_selector('div.location-address > p').get_attribute('textContent').split('\n')[2].split(',')[1].strip()[:2].strip()

            # city
            city = dealer.find_element_by_css_selector('div.location-address > p').get_attribute('textContent').split('\n')[2].split(',')[0].strip()

            # zip
            zipcode = dealer.find_element_by_css_selector('div.location-address > p').get_attribute('textContent').split('\n')[2].split(',')[1].strip()[2:].strip()

            # Lat
            lat = dealers_ll_dict[location_title][0]

            # Long
            lon = dealers_ll_dict[location_title][1]

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


