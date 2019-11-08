from xml.etree import cElementTree as ET
import requests

from Scraper import Scrape


URL = "http://haloburger.com/"


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
        headers = {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Referer': 'http://haloburger.com/locations.php',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }

        response = requests.get('http://haloburger.com/assets/halocations.xml', headers=headers, verify=False).content
        stores = self.etree_to_dict(ET.XML(response))['markers']['marker']

        for store in stores:
            # Store ID
            location_id = store['@storenum']

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = store['@category']

            # Name
            location_title = store['@name']

            # Street
            street_address = store['@address'] + store['@address2']

            # city
            city = store['@city']

            # zip
            zipcode = store['@postal']

            # State
            state = store['@state']

            # Phone
            phone = store['@phone']

            # Lat
            lat = store['@lat']

            # Long
            lon = store['@lng']

            # Hour
            hour = store['@hours1'] + ' ' + store['@hours2'] + ' ' + store['@hours3']

            # Country
            country = store['@country']

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
            page_urls.append(page_url)

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