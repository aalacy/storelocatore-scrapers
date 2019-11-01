import asyncio

import aiohttp
from Scraper import Scrape


URL = "https://sweetgreen.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.stores = []
        self.headers = {
            "sec-fetch-mode": "cors",
            "dnt": "1",
            "accept-encoding": "gzip, deflate, br",
            "x-csrf-token": "undefined",
            "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "x-requested-with": "XMLHttpRequest",
            "cookie": "_ga=GA1.2.988422949.1571895627; _gid=GA1.2.1147404022.1571895627; _gat=1; _gat_UA-8921332-12=1; _scid=9aacd3c4-3ef7-49e0-b886-c448cd956ec3; _fbp=fb.1.1571895626852.697795897; _sctr=1|1571814000000; _oprm=%7B%22t%22%3A%201574487627%2C%22s%22%3A%20%7B%22id%22%3A%20%22D3JL3Z6O0O6NDHH3KBN6ZD499CTJ8ZPJ%22%2C%22sc%22%3A%201%2C%22an%22%3A%20null%7D%7D; _session_id=f638cda6e75f9aedd2b0583186e982e8; _mibhv=anon-1571895631274-5192445193_7704; _micpn=esp:-1::1571895631274; _gcl_au=1.1.471898219.1571895631; _gat_UA-8921332-1=1; _gat_UA-8921332-9=1",
            "x-newrelic-id": "XQ4HWV5aGwsFXVhQAwk=",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "referer": "https://order.sweetgreen.com/?_ga=2.34243681.1147404022.1571895627-988422949.1571895627",
            "authority": "order.sweetgreen.com",
            "if-none-match": 'W/"9f985786629ffcea51eb80497e91dca4"',
            "sec-fetch-site": "same-origin",
        }

    async def get_locations(self, session, page):
        async with session.get(
            f"https://order.sweetgreen.com/api/restaurants?page={page}&per=1000"
        ) as response:
            response = await response.json()
            self.stores.extend(response["restaurants"])

    async def main(self):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[self.get_locations(session, page) for page in range(0, 2)]
            )

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

        asyncio.run(self.main())
        for store in self.stores:
            # Store ID
            location_id = store["asset_ids"][0]

            # Type
            location_type = (
                "sg Outpost" if "outpost" in store["name"].lower() else "Restaurant"
            )

            # Name
            location_title = store["name"]

            # Street
            street_address = store["address"]

            # city
            city = store["city"]

            # zip
            zipcode = store["zip_code"]

            # State
            state = store["state"]

            # Lat
            lat = store["latitude"]

            # Long
            lon = store["longitude"]

            # Phone
            phone = store["phone"]

            # Hour
            hour = (
                store["store_hours"]
                if store["store_hours"] and len(store["store_hours"].strip()) > 0
                else "<MISSING>"
            )

            # Country
            country = "US"

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
