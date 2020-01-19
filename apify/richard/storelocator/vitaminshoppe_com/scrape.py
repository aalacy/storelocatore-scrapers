import requests
import sgzip
import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.vitaminshoppe.com/"


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
        page_urls = []
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        headers = {
            'authority': 'maps.locations.vitaminshoppe.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'origin': 'https://locations.vitaminshoppe.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'dnt': '1',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'referer': 'https://locations.vitaminshoppe.com/?q=94587',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            '$cookie': '_gcl_au=1.1.2021699087.1575761122; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.1029605358.1575761123; _gid=GA1.2.1327116130.1575761123; rlsgeoipdat=%7B%22country_name%22%3A%22United+States%22%2C%22country_code%22%3A%22US%22%2C%22region%22%3A%22CA%22%2C%22city%22%3A%22Menlo+Park%22%2C%22postal_code%22%3A%2294025%22%2C%22latitude%22%3A37.4446%2C%22longitude%22%3A-122.1835%2C%22ip%22%3A%22199.201.64.137%22%7D; _gat_UA-3215593-1=1; bm_sz=011F0852C5D0C131BC45808B43AF184D~YAAQeLIbuPJRXHduAQAAwwGx4gbfbadWNwzpfCMxrAjnd0MtpI3aTjuooNzktMsD03lbSzv6gstQw628snzsDr/VSrmJ6ejGtSp+Q84TzylwA6qeJBo1ct1LKgRG5WmXM+qTYsG3++AaXIwWhd0jkE+3VOPvo8s6KdtG7YL7Wjmbi64xb3L7QWaMiBLCh3JK6cxMFBxtNQ==; optimizelyEndUserId=oeu1575761282451r0.41239630776336345; _abck=4AD737454EE9E3FE1A2F9DF28AAA526C~0~YAAQeLIbuPVRXHduAQAA1gax4gMmTUbMaS7ESmq3t//JRWwCBlYB8m5HqL5rJYzNIROraxD+fnElLz1uqnoJZZy3hy9gxn/fm/0Nzp/Vn4jZQU7pyxIpxb/fVqKMppBHGHRh5JZeXG6EFY8vcfmc44iA4Kj8oPC6Jb6CAujfoopy2Ns9FFCp8WI9WF2RP3EtmjxRVkULV/L6BcqVu8C9y9zp9DdB2Yy1vMrbrrryCJii4CHwPJXyzG6D7r4WQdU62g1lW+rQU0a8eqbngs0EhQoqT7hNcTN34DUpHc4CtcCAhw/NCSbkwEXbgfXAwWn5nVxRdkRgDZNDwBFL5CI=~-1~-1~-1; JSESSIONID=lLPisQd3Ojm30m4lrOr_ZINVOW7W4vLd9GSFOHfOkLdWhjD_cT3H\\u0021308003910; rr_session_id_value=u2369521062%7C1575761283081; rr_session_timeout=true; rr_user_id=u2369521062; ak_bmsc=AB45D3E6F8DCA0E3BF89555C391FE749B81BB278305600008135EC5D7BACB458~plikoBTPvRjl4JAQ/Ivfjnl5WRVhes2GbWzgsbvWxKGfPj4ydA0htoR314nLTFQJxOseG4Ned6NHCQzmY3V5YmW5nA68ATr7bZYGSW5trikxIrxrUfPEpsyrls5Bg7WNmt9izoiCdIxWaQYnfWAqhw6HjZRKsj+V+H9nWwGYSqSipcSCNnqz73XOxFPEGwDz2jeOJ3CiDWclB6gDmIS2SoUIVsdJW1O//wwpv2jKQnau8K2bTlNx48s5zqVCBMkqpu; bm_sv=6193E5A8EE8D1EE38572BDD92B5B0EB5~oFJqAVRe6mgznsRVt2k6WY3WwYp4kamH4JQ+QlDygCeqjta4p2eVIPr538eKd/y/hlu3kYfWFEjG3pPhWMVNGRJjosfBXqaZIYdXkuxohlfqxk4OC7R3xQtYpj2d+U8FgRlAH9qxOKs6OnoGvHw8lpJ0QhsM5ybaQIrID7r80QA=; _dc_gtm_UA-3215593-1=1; smtrrmkr=637113580869548140%5E016ee2b1-172b-40a3-97da-e71b6d5cb158%5E016ee2b1-172b-4674-aa03-3b7ec59ecbdc%5E%5E199.201.64.137; _derived_epik=dj0yJnU9emZVUE8yUmtGZFRJUmxyVWNtUEt5LWJydDREN1NNUDMmbj02WkI2bnhBUmRGRlZaZTByeU9RSHJnJm09NyZ0PUFBQUFBRjNzTllj; bc_pv_end=null; _gali=q',
        }

        for zip_search in sgzip.for_radius(50):
            params = (
                ('template', 'domain'),
                ('level', 'domain'),
                ('search', zip_search),
            )
            data = requests.get('https://maps.locations.vitaminshoppe.com/api/getAsyncLocations', headers=headers, params=params).json()['markers']
            if data:
                stores.extend(data)
                print(f"{len(data)} locations scraped for {zip_search}")

        for store in stores:
            store = json.loads(store['info'].replace('<div class="tlsmap_popup">', '').replace('</div>', ''))
            if store['fid'] not in self.seen:
                driver.get(store['url'])

                print(f"Getting additional information for {store['url']}")

                # Store ID
                location_id = store['fid']

                # Name
                location_title = f"{store['location_name']} - {store['location_display_name']}"

                # Page url
                page_url = store['url']

                # Type
                location_type = 'Retail'

                # Street
                street_address = (store['address_1'] + ' ' + store['address_2']).strip()

                # city
                city = store['city']

                # zip
                zipcode = driver.find_element_by_css_selector('p.address').get_attribute('textContent').strip()[-5:]

                # State
                state = store['url'].split('/')[-1].replace('.html', '').replace(f"-{location_id}", '')[-2:].upper()

                # Phone
                phone = driver.find_element_by_css_selector('a.phone.gaq-link').text

                # Lat
                lat = store['lat']

                # Long
                lon = store['lng']

                # Hour
                hour = driver.find_element_by_css_selector('div.hours').get_attribute('textContent')

                # Country
                country = 'US'

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
                self.seen.append(location_id)

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
