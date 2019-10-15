import json
import requests

from pypostalcode import PostalCodeDatabase
from Scraper import Scrape


URL = "http://www.jiffylube.ca"


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
        stores = []

        url = 'http://www.jiffylube.ca/Locations/GeocodeAddress'

        pcdb = PostalCodeDatabase()
        pc = 'T3Z'
        radius = 3000
        results = pcdb.get_postalcodes_around_radius(pc, radius)
        postalcodes = [p.postalcode for p in results]

        for postalcode in postalcodes:
            data = {
                'fieldValue': postalcode
            }

            r = requests.post(
                url=url,
                data=data
            )
            stores.extend(json.loads(r.content)['Stores'])

        for store in stores:
            if store["Store_Number"] not in self.seen:
                # Store ID
                location_id = store["Store_Number"]

                # Name
                location_title = 'Jiffy Lube'

                # Type
                location_type = '<MISSING>'

                # Street
                street_address = store["Address_Line_1"] + store["Address_Line_2"]

                # State
                state = store["Region_State"]

                # city
                city = store["City"]

                # zip
                zipcode = store["Postal_Code"]

                # Lat
                lat = store['Latitude']

                # Long
                lon = store['Longitude']

                # Phone
                phone = store["Phone_Number"]

                # Hour
                hour = store["StoreHoursCollection"]

                # Country
                country = store['Country']

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
                self.seen.append(location_id)

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
