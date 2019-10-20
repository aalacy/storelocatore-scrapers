from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://miravalresorts.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.block = ['https://www.miravalstkitts.com/']
        self.exceptions = {
            "https://www.miravalspamonarchbeach.com/": {
                "title": "Miraval Life in Balance Spa - Monarch Beach",
                "address": "One Monarch Beach Resort",
                "city": "Dana Point",
                "state": "California",
                "zip": "92629",
                "number": "800-722-1543"
            }
        }
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

        location_url = 'https://www.miravalresorts.com/'
        driver.get(location_url)
        stores = [info.get_attribute('href') for info in driver.find_elements_by_css_selector('div.modal--row > div.modal--column > ul > li > a')]

        for store in stores:
            store = store.strip()
            if store not in self.block and store not in self.exceptions and store not in self.seen:
                print(f"Now scraping {store}")
                driver.get(store)

                loc_info = driver.find_element_by_css_selector('div.footer--column > p').get_attribute('innerHTML').split('<br>')
                latlng_info  = [script for script in driver.find_elements_by_css_selector('head.at-element-marker > script')]
                # script_data = [info for info in latlng_info  if info.get_attribute('type') == 'application/ld+json']
                # latlng_data = json.loads(re.sub('<script.+>', '', script_data[-1].get_attribute('outerHTML').replace('</script>', '')))

                self.seen.append(store)
                # Store ID
                location_id = '<MISSING>'

                # Type
                location_type = 'Wellness and Resort'

                # Name
                location_title = loc_info[0]

                # Street
                street_address = loc_info[1].split(',')[0].strip()

                # city
                if len(loc_info[2].split(',')) == 1:
                    city = loc_info[1].split(',')[1].strip()
                else:
                    city = loc_info[2].split(',')[0]

                # zip
                zipcode = loc_info[2].strip()[-5:]

                # State
                state = loc_info[2].strip()[:-5].split(',')[-1].strip()

                try:
                    # Phone
                    phone = driver.find_element_by_css_selector('a.call-button > noscript').get_attribute('textContent')
                except:
                    phone = '<MISSING>'

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Hour
                hour = 'Always Open'

                # Country
                country = 'USA'

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

            elif store in self.exceptions.keys() and store not in self.seen:
                print(f"Now scraping {store}")

                # Store ID
                location_id = '<MISSING>'

                # Type
                location_type = 'Wellness and Resort'

                # Name
                location_title = self.exceptions[store]['title']

                # Street
                street_address = self.exceptions[store]['address']

                # city
                city = self.exceptions[store]['city']

                # zip
                zipcode = self.exceptions[store]['zip']

                # State
                state = self.exceptions[store]['state']

                # Phone
                phone = self.exceptions[store]['number']

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Hour
                hour = 'Always Open'

                # Country
                country = 'USA'

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
                self.seen.append(store)


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
