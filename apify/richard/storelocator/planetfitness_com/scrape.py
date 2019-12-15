import requests

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.planetfitness.com/"


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
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        headers = {
            'authority': 'www.planetfitness.com',
            'accept': 'application/json, text/plain, */*',
            'dnt': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.planetfitness.com/gyms/?q=canada',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            '$cookie': '__cfduid=d41ddbb55286d6e7de99999b98a6220281575263471; _ga=GA1.2.1147394816.1575263472; _gid=GA1.2.428937504.1575263472; _gcl_au=1.1.569666395.1575263472; _hjid=9c1b3f43-0589-4c9b-9c76-8caa79355d4a; _fbp=fb.1.1575263472702.1011105261; _csrf-pf-website=ABc4yUqYy4WoalhncBeVxnQK; _gaexp=GAX1.2.OwyFdkNJRtycE5PJS_QboQ.18278.0\\u0021OawPFZ36QEGoViqVwLKHhQ.18290.1; pfx_join_experience=new; _dc_gtm_UA-27725796-5=1; _derived_epik=dj0yJnU9YXlPZThYRDkzX082RHUzanAzTVQ2ZWFWRjJ6em9xUTMmbj11emVrOWVUWEk1cHB6UnRrTVppbTJnJm09NyZ0PUFBQUFBRjNsX0pZ; AWSALB=VFmb30Ovg5W4m4c0zekTQTNhO0ZqB4APf9a21Ytw6Vj0ER3oPi9JGLIZMdIr2cRdNqAwubaygFmuTdl7TMERZnIaTW7x8RrLDZJf6OsfBZaWAluB2zYvxzH/bO/N',
        }

        params = (
            ('lat', '39.002064545536115'),
            ('long', '-101.84003662167544'),
            ('limit', '200000000'),
            ('distance', '999999999999'),
        )

        stores.extend(requests.get('https://www.planetfitness.com/gyms/pfx/api/clubs/', headers=headers, params=params).json()['clubs'])

        for store in stores:
            if store['status'] in ['OPEN', 'OPEN_RECENTLY'] and store['location']['address']['countryCode'] in ['US', 'CA']:
                print(f"Getting location information for {'https://www.planetfitness.com/gyms/' + store['slug']}")

                # Store ID
                location_id = store['pfClubId']

                # Name
                location_title = store['name']

                # Page url
                page_url = 'https://www.planetfitness.com/gyms/' + store['slug']
                driver.get(page_url)

                # Type
                location_type = 'Gym'

                # Street
                street_address = store['location']['address']['line1']

                # city
                city = store['location']['address']['city']

                # zip
                zipcode = store['location']['address']['postalCode']

                # State
                state = store['location']['address']['stateCode']

                # Phone
                phone = store['telephone']

                # Lat
                lat = store['location']['latitude']

                # Long
                lon = store['location']['longitude']

                # Hour
                hour = driver.find_element_by_css_selector('div.columns.small-12.medium-6 > p').get_attribute('textContent')

                # Country
                country = store['location']['address']['countryCode']

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
