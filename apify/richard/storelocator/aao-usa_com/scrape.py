import json

import requests
import sgzip
from Scraper import Scrape
from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
import re

logger = SgLogSetup().get_logger("aao-usa_com")

URL = "https://aao-usa.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []
        self.exceptions = {
            "200 Baychester Ave, The Bronx, NY 10475": {
                "street_address": "200 Baychester Ave",
                "city": "The Bronx",
                "state": "NY",
                "zip": "10475",
                "country": "USA",
            },
            "250 Woodbridge Center Drive Woodbridge NJ 07095": {
                "street_address": "250 Woodbridge Center Drive",
                "city": "Woodbridge",
                "state": "NJ",
                "zip": "07095",
                "country": "USA",
            },
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
        stores = []
        page_urls = []

        url = "https://shopaao.com/AAOStoreLocators/index.php"
        sgcoord = static_coordinate_list(
            radius=200, country_code=SearchableCountries.USA
        )

        for coords in sgcoord:
            data = {
                "ajax": "1",
                "action": "get_nearby_stores",
                "distance": "200",
                "lat": coords[0],
                "lng": coords[1],
            }
            headers = {"cookie": "PHPSESSID=5deb3c76a4d67a494af32b91957192d5"}
            r = requests.post(url=url, data=data, headers=headers)
            decoded_data = r.text.encode().decode("utf-8-sig")
            data = (
                json.loads(decoded_data)["stores"]
                if "stores" in json.loads(decoded_data).keys()
                else []
            )
            stores.extend(data)
            logger.info(
                f"{len(data)} stores scraped for coords Lat: {coords[0]} Long:  {coords[1]}"
            )
        for store in stores:
            if store["name"] not in self.seen:
                # Store ID
                location_id = "<MISSING>"
                page_url = "https://aao-usa.com/pages/aao-store-locator"
                # Name
                location_title = store["name"]

                # Type
                location_type = "<MISSING>"

                # Street
                if store["address"] in self.exceptions:
                    street_address = self.exceptions[store["address"]]["street_address"]
                    city = self.exceptions[store["address"]]["city"]
                    state = self.exceptions[store["address"]]["state"]
                    zipcode = self.exceptions[store["address"]]["zip"]
                    country = self.exceptions[store["address"]]["country"]
                else:
                    street_address = " ".join(store["address"].split(",")[:-4])
                    if len(store["address"].split(",")) > 4:

                        # State
                        state = store["address"].split(",")[-3]

                        # city
                        city = store["address"].split(",")[-4]

                        # zip
                        zipcode = store["address"].split(",")[-2]

                        # Country
                        country = store["address"].split(",")[-1]
                    else:
                        temp_address = store["address"]
                        pattern = "space# \d{4,5}"
                        temp_address = re.sub(pattern, ",", temp_address)
                        temp_address = temp_address.split(",")
                        street_address = temp_address[0]
                        city = temp_address[1]
                        state = temp_address[2].split(" ")[1]
                        zipcode = temp_address[2].split(" ")[2]
                # Lat
                lat = store["lat"]

                # Long
                lon = store["lng"]

                # Phone
                phone = store["telephone"]

                # Hour
                hour = "<MISSING>"

                # Store data
                locations_ids.append(location_id)
                page_urls.append(page_url)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                states.append(state.lstrip())
                zip_codes.append(zipcode.lstrip())
                hours.append(hour)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                cities.append(city.lstrip())
                countries.append(country.lstrip())
                location_types.append(location_type)
                self.seen.append(location_title)
        for (
            page_url,
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
            page_urls,
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
