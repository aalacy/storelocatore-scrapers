import csv
import requests
import json


COMPANY_URL = "https://handelsicecream.com"


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
    zip_codes = []
    countries = []
    phone_numbers = []
    latitude_list = []
    longitude_list = []
    hours = []
    data = []

    stores = json.loads(requests.get("https://handelsicecream.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=342475a0ef&load_all=1&layout=1").content)

    for store in stores:
        # Store id
        locations_id.append(store['id'])

        # Store title
        locations_titles.append(store['title'])

        # Street
        street_addresses.append(store['street'])

        # city
        cities.append(store['city'])

        # State
        states.append(store['state'])

        # zip codes
        zip_codes.append(store['postal_code'])

        # Country
        countries.append(store['country'])

        # Lat
        latitude_list.append(store['lat'])

        # lng
        longitude_list.append(store['lng'])

        # Phone
        phone_numbers.append(store['phone'])

        # hour
        hours.append(''.join([key + ': ' + value + '\n' for key, value in json.loads(store['open_hours']).items()]))

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
            hour
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
        hours
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