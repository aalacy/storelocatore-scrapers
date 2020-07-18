import re
import json
import sgzip
from sgrequests import SgRequests
from Scraper import Scrape

URL = "https://www.vw.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []

    def fetch_data(self):
        session = SgRequests()
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
        dealers = []
        seen = []

        # Fetch stores from location menu
        for zip_search in sgzip.for_radius(50):
            location_url = "https://www.vw.com/vwsdl/rest/product/dealers/zip/{0}.json".format(zip_search)
            
            response = session.get(location_url)
            if response.status_code == 200:
                data = response.json()
                dealers.extend(data.get('dealers', []))

        for dealer in dealers:
            # Store ID
            location_id = dealer["dealerid"]

            # Name
            location_title = dealer["name"]

            # Street
            street_address = (dealer["address1"] + " " + dealer["address2"]).strip()

            # Country
            country = dealer["country"]

            # State
            state = dealer["state"]

            # city
            city = dealer["city"]

            # zip
            zipcode = dealer["postalcode"]

            # Lat
            lat = dealer["latlong"].split(",")[0]

            # Long
            lon = dealer["latlong"].split(",")[1]

            # Phone
            phone = dealer["phone"]

            # hour
            regex = re.compile("sale", re.IGNORECASE)
            department_hours = dealer["hours"]
            sale_department = next((x for x in department_hours if regex.match(x.get('departmentName'))), None)

            sale_hours = sale_department.get('departmentHours', '<MISSING>') if sale_department else '<MISSING>'

            # Store data
            locations_ids.append(location_id)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zipcode)
            hours.append(sale_hours)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)

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
            if location_id not in seen:
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
                seen.append(location_id)


scrape = Scraper(URL)
scrape.scrape()
