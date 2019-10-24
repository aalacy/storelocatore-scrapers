import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.myidealdental.com/"


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

        location_url = 'https://www.myidealdental.com/dentist-offices/'
        driver.get(location_url)
        stores = [info.get_attribute('href') for info in driver.find_elements_by_css_selector('div.cta-wrapper > a.no-print')]

        for store in stores:
            driver.get(store)
            data = json.loads([info.get_attribute('outerHTML') for info in driver.find_elements_by_css_selector('script') if info.get_attribute('type') == 'application/ld+json'][0].replace('<script type="application/ld+json">', '').replace('</script>', ''))

            # Store ID
            location_id = '<MISSING>'

            # Type
            location_type = data['@type']

            # Name
            location_title = data['name']

            # Street
            street_address = data['address']['streetAddress']

            # city
            city = data['address']['addressLocality']

            # zip
            zipcode = data['address']['postalCode']

            # State
            state = data['address']['addressRegion']

            # Phone
            phone = data['contactPoint'][0]['telephone']

            # Lat
            lat = data['geo']['latitude']

            # Long
            lon = data['geo']['longitude']

            # Hour
            hour = ' '.join([f"{info['dayOfWeek']}: Opens at {info['opens']}, Closes at {info['closes']}" for info in data['openingHoursSpecification'] if 'opens' in info.keys()])

            # Country
            country = data['address']['addressCountry']

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