import requests
import json
import sgzip

from Scraper import Scrape
from bs4 import BeautifulSoup


URL = "https://www.habitat.org/"


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
        page_urls = []
        location_types = []

        for zipcode in sgzip.for_radius(50):
            while True:
                counter = 1
                try:
                    data = requests.get(f'https://www.habitat.org/local/restore?zip={zipcode}').content
                    data = BeautifulSoup(data, features="lxml").find('script', {'type': 'application/json', 'data-drupal-selector': 'drupal-settings-json'})
                    stores  = json.loads(data.text)['gMaps'][0]['markers'] if 'gMaps' in json.loads(data.text).keys() else []
                    break
                except:
                    counter += 1
                    pass

            for store in stores:
                if store['title'] not in self.seen:
                    # Store ID
                    location_id = '<MISSING>'

                    # Type
                    location_type = '<MISSING>'

                    # Page url
                    page_url = '<MISSING>'

                    # Name
                    location_title = store['title']

                    # Street
                    street_address = ' '.join(store['details']['desc'].replace('</p><p>', ',').replace('<p>', '').replace('</p>', '').split(',')[:-2]) if len(store['details']['desc']) > 0 else '<MISSING>'

                    # city
                    city = store['details']['desc'].replace('</p><p>', ',').replace('<p>', '').replace('</p>', '').split(',')[-2].strip() if len(store['details']['desc']) > 0 else '<MISSING>'

                    # zip
                    zipcode = store['details']['desc'].replace('</p><p>', ',').replace('<p>', '').replace('</p>', '').split(',')[-1][-5:].strip() if len(store['details']['desc']) > 0 else '<MISSING>'

                    # State
                    state = store['details']['desc'].replace('</p><p>', ',').replace('<p>', '').replace('</p>', '').split(',')[-1][:-5].strip() if len(store['details']['desc']) > 0 else '<MISSING>'
                    # Lat
                    lat = store['position']['lat']

                    # Long
                    lon = store['position']['lng']

                    # Phone
                    phone = store['details']['phone']

                    # Hour
                    hour = '<MISSING>'

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
                    self.seen.append(location_title)

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