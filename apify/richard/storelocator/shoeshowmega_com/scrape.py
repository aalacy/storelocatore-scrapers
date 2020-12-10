from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip
from sgzip import SearchableCountries
import csv
import re

URL = "shoeshowmega.com"


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    data = []

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    zips = sgzip.for_radius(radius=100, country_code=SearchableCountries.USA)

    for zip_search in zips:
        location_url = f'https://www.shoeshowmega.com/on/demandware.store/Sites-shoe-show-Site/default/Stores-FindStores?showMap=true&radius=10000&postalCode={zip_search}'
        stores = session.get(location_url, headers = HEADERS).json()['stores']

        for store in stores:
            # Store ID
            location_id = store['ID']

            if location_id in found_poi:
                continue

            found_poi.append(location_id)
            # Name
            location_title = store['name']

            # Street Address
            try:
                street_address = (store['address1'] + " " + store['address2']).strip()
            except:
                street_address = store['address2']
                if not street_address:
                    street_address = store['address1']

            digit = re.search("\d", street_address).start(0)
            if digit != 0:
                street_address = street_address[digit:]

            if street_address.split()[0].strip().isdigit() and street_address.split()[1].strip().isdigit():
                street_address = street_address[street_address.find(" "):].strip()
                
            # City
            city = store['city']

            # State
            state = store['stateCode']

            # Zip
            zip_code = store['postalCode']

            # Hours
            hour = store['storeHours']
            hour = " ".join(list(BeautifulSoup(hour,"lxml").stripped_strings)).split("Open Daily - Special")[0].strip()
            hour = (re.sub(' +', ' ', hour)).strip()

            # Lat
            lat = store['latitude']

            # Lon
            lon = store['longitude']

            # Phone
            phone = store['phone']

            # Country
            country = store['countryCode']

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
        data.append(
            [
                URL,
                "<MISSING>",
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

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
