import csv
import requests
import json
import re


COMPANY_URL = "https://www.lotuscars.com"


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

    dealers = json.loads(requests.get("https://www.lotuscars.com/app/wp-admin/admin-ajax.php?action=dealer_map_load").content)

    for dealer in dealers:
        if dealer['country'] in ['US', 'CA']:
            # Name
            locations_titles.append(dealer['name'])

            # ID
            locations_id.append(dealer['id'])

            # Street address
            street_addresses.append(re.sub('<[^>]*>', ',', dealer['address']).strip().split(',')[0].strip())

            # City
            cities.append(re.sub('<[^>]*>', ',', dealer['address']).strip().split(',')[1].strip())

            # State
            states.append(re.sub('<[^>]*>', ',', dealer['address']).strip().split(',')[2].strip())

            # Zip code
            zip_codes.append(re.sub('<[^>]*>', ',', dealer['address']).strip().split(',')[3].strip())

            # Country
            countries.append(dealer['country'])

            # Phone
            if dealer['phone']:
                phone_numbers.append(dealer['phone'][0]['number'])
            else:
                phone_numbers.append('<MISSING>')

            # Lat
            latitude_list.append(dealer['location']['lat'])

            # long
            longitude_list.append(dealer['location']['lng'])

            # Hour
            if dealer['opening_times']:
                hours.append(re.sub('<[^>]*>', '\n', dealer['opening_times'][0]['times']))
            else:
                hours.append('<MISSING>')


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