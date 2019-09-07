import csv
import requests

COMPANY_URL = "https://www.childrenslearningadventure.com"

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
    location_id = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    hours = []
    longitude_list = []
    latitude_list = []
    data = []

    # curl
    url = 'https://www.childrenslearningadventure.com/scripts/find-locations.php'
    headers = {
        'sec-fetch-mode': 'cors',
        'dnt': '1',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://www.childrenslearningadventure.com/index.php/locations',
        'authority': 'www.childrenslearningadventure.com',
        'sec-fetch-site': 'same-origin',
        'origin': 'https://www.childrenslearningadventure.com',

        'cookie': '_gcl_au=1.1.1038657872.1565665535; _ga=GA1.2.850675706.1565665535; _fbp=fb.1.1565665535373.1665532306; comm100_guid2_220027=K3aRJI-s8EqjUqiksEfWzQ; calltrk_referrer=direct; calltrk_landing=https%3A//www.childrenslearningadventure.com/; calltrk_session_id=d9753a91-114d-4d6a-b72d-b65b655827a3; hubspotutk=80152a9cee431022d31e7223ba4e19bb; __hssrc=1; PHPSESSID=bbljuigp8ijaclk0ap5qmp5hq1; _gid=GA1.2.95347558.1565817899; _gat_UA-34750246-1=1; __hstc=88545348.80152a9cee431022d31e7223ba4e19bb.1565665539199.1565671483291.1565817902703.3; __hssc=88545348.2.1565817902703',
    }
    payload = {
        'state': '',
        'city': '',
        'zipcode': '',
        'miles': 1000,
        'format-as': 'json'
    }

    locations = requests.post(url, data = payload, headers = headers).json()['json']['locations']

    for location in locations.values():
        # Title
        locations_titles.append(location['title'])

        # location id
        location_id.append(location['cms_id'])

        # Address
        street_addresses.append(location['address'])

        # City
        cities.append(location['city'])

        # state
        states.append(location['state'])

        # phone
        phone_numbers.append(location['phone1'])

        # Zip
        zip_codes.append(location['zip'])

        # lat
        latitude_list.append(location['lat'])

        # lon
        longitude_list.append(location['lon'])

    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            latitude,
            longitude,
            id
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        location_id
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
                id,
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                '<MISSING>',
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()