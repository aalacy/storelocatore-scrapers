import requests

from datetime import datetime
from Scraper import Scrape

URL = "https://www.elpolloloco.com/"


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
        page_urls = []

        cookies = {
            'opvc': '298bde4b-6893-4f5d-ad62-f3ad8707166c',
            'sitevisitscookie': '1',
            'dmid': '8d17f78a-218f-4208-8c95-d39f54bc16ab',
            '_gcl_au': '1.1.1137056012.1571548098',
            '_ga': 'GA1.2.181724118.1571548099',
            '_fbp': 'fb.1.1571548099618.1073523732',
            'JSESSIONID': '20301CBC38E1E34F80A1F3491724EC03',
            '_gid': 'GA1.2.89283643.1572067777',
            '_gat_UA-136265182-1': '1',
            'HideWelcomeMat': 'Fri Oct 25 2019 22:29:40 GMT-0700 (Pacific Daylight Time)',
        }

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://www.elpolloloco.com/locations/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        response = requests.get('https://www.elpolloloco.com/locations/locations_json', headers=headers, cookies=cookies)
        stores = response.json()

        for store in stores:
            if datetime.strptime(store[10], '%Y-%m-%d %H:%M:%S.%f') <= datetime.now():
                # Store ID
                location_id = store[0]

                # Page url
                page_url = '<MISSING>'

                # Type
                location_type = 'Restaurant'

                # Name
                location_title = f'El Pollo Loco - {store[3]}'

                # Street
                street_address = store[1] + store[2]

                # city
                city = store[3]

                # zip
                zipcode = store[5]

                # State
                state = store[4]

                # Phone
                phone = store[6]

                # Lat
                lat = store[8]

                # Long
                lon = store[9]

                # Hour
                hour = ' '.join(store[13]) if len(' '.join(store[13]).strip()) != 0 else '<MISSING>'

                # Country
                country = store[15].split('/')[0]

                # Store data
                locations_ids.append(location_id)
                page_urls.append(page_url)
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
                page_url,
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
            page_urls,
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
            self.data.append(
                [
                    self.url,
                    page_url,
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
