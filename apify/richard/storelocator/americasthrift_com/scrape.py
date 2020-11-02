import csv
import requests
import re


COMPANY_URL = "https://www.americasthrift.com"


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
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    hours = []
    longitude_list = []
    latitude_list = []
    stores_type = []
    data = []


    # curl
    url = 'https://www.americasthrift.com/wp-admin/admin-ajax.php'
    headers = {
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*',
        'Referer': 'https://www.americasthrift.com/locations/',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': '_ga=GA1.3.995751209.1565807384; _gid=GA1.3.1488490346.1565807384; _fbp=fb.1.1565807384484.382450588; _ga=GA1.2.995751209.1565807384; _gid=GA1.2.1488490346.1565807384',
        'Connection': 'keep-alive'
    }
    payload = {
        'action': 'get_json_data',
        'type': 'stores',
        'nonce': 'b354001cb7'
    }

    locations = requests.post(url, data = payload, headers = headers).json()

    for location in locations:
        # location name
        locations_titles.append(location['ib_name'])

        # Address
        street_addresses.append(location['box_address']  + location['street_address_2'])

        # City
        cities.append(location['box_city'])

        # State
        states.append(location['box_state'])

        # Zipcode
        zip_codes.append(location['box_zip'])

        # phone
        phone_numbers.append(re.sub('<[^>]*>', '', location['phone_number']))

        # hours
        hours.append(re.sub('<[^>]*>', '', location['hours']))

        # Lat
        latitude_list.append(location['latitude'])

        # Longitude
        longitude_list.append(location['longitude'])

        # Store type
        stores_type.append(location['ib_type'])


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
            store_type,
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
        stores_type,
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                'US',
                "<MISSING>",
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