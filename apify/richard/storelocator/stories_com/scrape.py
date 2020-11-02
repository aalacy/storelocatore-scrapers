import csv
import requests
import json

COMPANY_URL = "https://www.stories.com/"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
    locations_id = []
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    stores_type = []
    zip_codes = []
    countries = []
    phone_numbers = []
    latitude_list = []
    longitude_list = []
    hours = []
    data = []

    stores = json.loads(requests.get("https://api.storelocator.hmgroup.tech/v2/brand/os/stores/locale/en_GB/country/US?openinghours=true&campaigns=true&departments=true").content)['stores']


    for store in stores:
        # Store ID
        locations_id.append(store['storeCode'])

        # Store type
        stores_type.append(store['storeClass'])

        # Location name
        locations_titles.append(store['name'])

        # Phone
        phone_numbers.append(store['phone'])

        # address
        street_addresses.append(store['address']['streetName1'] + ' ' + store['address']['streetName2'])

        # City
        cities.append(store['address']['postalAddress'])

        # State
        states.append(store['address']['state'])

        # Zip
        zip_codes.append(store['address']['postCode'])

        # Country
        countries.append(store['country'])

        # Latitude
        latitude_list.append(store['latitude'])

        # Longitude
        longitude_list.append(store['longitude'])

        # Hour
        hour = ' '.join([day_time['name'] + ': Opens at ' + day_time['opens'] + ' Closes at ' + day_time['closes'] for day_time in store['openingHours']])
        hours.append(hour)

    # Store data
    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            country,
            latitude,
            longitude,
            location_id,
            hour,
            store_type
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        countries,
        latitude_list,
        longitude_list,
        locations_id,
        hours,
        stores_type
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                country,
                location_id,
                phone_number,
                store_type,
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