import json
from Scraper import Scrape  # noqa: I900
from sgrequests import SgRequests
from bs4 import BeautifulSoup as BS

URL = "https://www.clement.ca/"
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.pc_lookup = {
            "G": "QC",
            "H": "QC",
            "J": "QC",
            "K": "ON",
            "L": "ON",
            "M": "ON",
            "N": "ON",
            "P": "ON",
        }

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

        location_url = "https://www.clement.ca/en/retailers/ajax/listretailer/"
        stores_req = session.get(location_url, headers=headers)
        stores = json.loads(stores_req.text.strip())

        for store in stores:
            # Store ID
            location_id = store["retailer_id"]

            # Name
            location_title = store["name"]

            # Type
            location_type = "<MISSING>"

            # Street
            street_address = store["street"]

            # city
            city = store["city"]

            # zip
            zipcode = store["postcode"]

            # State
            state = self.pc_lookup[zipcode[0]]

            # Lat
            lat = store["latitude"]

            # Long
            lon = store["longitude"]

            # Phone
            phone = store["phone"]

            # Hour
            hour = "; ".join(
                BS(store["opening_hours"], "lxml")
                .get_text()
                .replace("*Mask mandatory", "")
                .split("\n")
            ).strip()

            # Country
            country = store["country_id"]

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
                        "<MISSING>",
                    ]
                )


scrape = Scraper(URL)
scrape.scrape()
