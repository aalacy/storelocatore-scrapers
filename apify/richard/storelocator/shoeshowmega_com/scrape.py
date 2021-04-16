import csv
import re

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

URL = "shoeshowmega.com"

log = sglog.SgLogSetup().get_logger(logger_name=URL)


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
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
    found_poi = []

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    max_distance = 1000

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
    )

    for zip_search in search:
        location_url = (
            "https://www.shoeshowmega.com/on/demandware.store/Sites-shoe-show-Site/default/Stores-FindStores?showMap=true&radius=%s&postalCode=%s"
            % (max_distance, zip_search)
        )
        log.info(location_url)
        stores = session.get(location_url, headers=headers).json()["stores"]

        for store in stores:
            # Store ID
            location_id = store["ID"]

            if location_id in found_poi:
                continue

            found_poi.append(location_id)
            # Name
            location_title = store["name"]

            # Street Address
            try:
                street_address = (store["address1"] + " " + store["address2"]).strip()
            except:
                street_address = store["address2"]
                if not street_address:
                    street_address = store["address1"]

            digit = re.search(r"\d", street_address).start(0)
            if digit != 0:
                street_address = street_address[digit:]

            if (
                street_address.split()[0].strip().isdigit()
                and street_address.split()[1].strip().isdigit()
            ):
                street_address = street_address[street_address.find(" ") :].strip()

            # City
            city = store["city"]

            # State
            state = store["stateCode"]

            # Zip
            zip_code = store["postalCode"]

            # Hours
            hour = store["storeHours"].split("<br><br")[0]
            hour = (
                " ".join(list(BeautifulSoup(hour, "lxml").stripped_strings))
                .split("Open Daily - Special")[0]
                .strip()
            )
            hour = (re.sub(" +", " ", hour)).strip()

            # Lat
            lat = store["latitude"]

            # Lon
            lon = store["longitude"]

            try:
                search.found_location_at(lat, lon)
            except:
                pass

            # Phone
            phone = store["phone"]

            # Country
            country = store["countryCode"]

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
        yield [
                URL,
                "https://www.shoeshowmega.com/stores",
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

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
