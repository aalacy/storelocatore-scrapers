from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "http://yangchow.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []
        self.postal_codes = []

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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'http://yangchow.com/'
        driver.get(location_url)
        stores = driver.find_elements_by_css_selector('tbody > tr:nth-of-type(9) > td')
        index = 0

        for store in stores:
            if index % 2 == 0 and index < 6:

                info = store.text.split('\n')

                location_id = '<MISSING>'

                locations_title = info[0]

                street_address = info[1]

                city = info[2].split(',')[0]

                state = info[2].split(',')[1].strip()[:-5]

                country = 'US'

                zip_code = info[2].split(',')[1].strip()[-5:]

                phone_number = info[3]

                hour = '<MISSING>'

                lat = '<MISSING>'

                lon = '<MISSING>'

                locations_ids.append(location_id)
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

            index += 1

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
