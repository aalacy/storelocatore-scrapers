import csv

from sgrequests import SgRequests

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
                "page_url",
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
    longitude_list = []
    latitude_list = []
    url_list = []
    data = []

    # curl
    url = "https://www.childrenslearningadventure.com/scripts/find-locations.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    payload = {
        "postback": "yes",
        "state": "",
        "city": "",
        "zipcode": "",
        "miles": 1000,
        "format-as": "json",
    }

    locations = session.post(url, data=payload, headers=headers).json()["json"][
        "locations"
    ]

    for location in locations.values():
        # Title
        locations_titles.append(location["title"])

        # location id
        location_id.append(location["cms_id"])

        # Address
        street_addresses.append(location["address"])

        # City
        cities.append(location["city"])

        # state
        states.append(location["state"])

        # phone
        phone_numbers.append(location["phone1"])

        # Zip
        zip_codes.append(location["zip"])

        # lat
        latitude_list.append(location["lat"])

        # lon
        longitude_list.append(location["lon"])

        # page_url
        url_list.append(COMPANY_URL + location["link"])

    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        latitude,
        longitude,
        id,
        page_url,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        location_id,
        url_list,
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                "US",
                id,
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                "<MISSING>",
                page_url,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
