import requests
import sgzip
from Scraper import Scrape


URL = "https://tigerrockmartialarts.com"


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
        stores = []

        headers = {
            "sec-fetch-mode": "cors",
            "cookie": "cxssh_status=off; PHPSESSID=a6db8e7ae9dc3117239141744f1a6c6f",
            "dnt": "1",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "referer": "https://tigerrockmartialarts.com/locations/?l=94587",
            "authority": "tigerrockmartialarts.com",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-site": "same-origin",
        }

        for zip_search in sgzip.for_radius(200):
            params = (("geolocate", zip_search), ("radius", "400"))

            response = requests.get(
                "https://tigerrockmartialarts.com/", headers=headers, params=params
            ).json()
            data = response["locations"] if "locations" in response.keys() else []
            stores.extend(data)
            print(f"{len(data)} locations scraped for {zip_search}")

        for store in stores:
            if store["location_id"] not in self.seen:
                # Store ID
                location_id = store["location_id"]

                # Name
                location_title = store["name"]

                # Street Address
                street_address = store["location_address"]

                # City
                city = store["location_city"]

                # State
                state = store["location_state"]

                # Zip
                zip_code = store["location_zip"]

                # Hours
                hour = "<MISSING>"

                # Lat
                lat = store["lat"]

                # Lon
                lon = store["lng"]

                # Phone
                phone = store["location_phone"]

                # Country
                country = "US"

                # Store data
                locations_ids.append(location_id)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                states.append(state)
                zip_codes.append(zip_code)
                hours.append(hour)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                cities.append(city)
                countries.append(country)
                self.seen.append(store["location_id"])

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


scrape = Scraper(URL)
scrape.scrape()
