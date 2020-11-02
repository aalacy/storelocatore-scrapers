import requests

from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mortensondental_com')




URL = "https://mortensondental.com"


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

        cookies = {
            'wordpress_google_apps_login': '287741313c3b0b36a76544038bd880ba',
            '_gcl_au': '1.1.1894753252.1570942647',
            '_ga': 'GA1.2.692126775.1570942647',
            '_gid': 'GA1.2.1538442416.1570942647',
            '_gat_UA-60067349-5': '1',
            '_fbp': 'fb.1.1570942647125.1127082472',
        }

        headers = {
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://mortensondental.com/locations/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        params = (
            ('origAddress', "40217"),
        )
        data = requests.get('https://mortensondental.com/wp-content/plugins/mdp-locations/data/mdpLocations_site1.json', headers=headers, params=params, cookies=cookies).json()
        stores.extend(data)
        logger.info(f"{len(data)} locations scraped")


        for store in stores:
            # Store ID
            location_id = store['id']

            # Type
            location_type = 'Dental Clinic'

            # Name
            location_title = store['name']

            # Street
            street_address = store['address']

            # city
            city = store['city']

            # zip
            zipcode = store['postal']

            # State
            state = store['state']

            # Phone
            phone = store['phone']

            # Lat
            lat = store['lat']

            # Long
            lon = store['lng']

            # Hour
            hour = '\n'.join([f"{hour['day']}: {hour['begin']} to {hour['end']}" for hour in store['hours'] if hour['begin'] != ""])

            # Country
            country = 'US'

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



scrape = Scraper(URL)
scrape.scrape()
