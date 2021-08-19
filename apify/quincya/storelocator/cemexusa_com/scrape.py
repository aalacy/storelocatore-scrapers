import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    api_link = "https://www.cemexusa.com/documents/27329108/45560536/places-usa.json/d5c682be-7d3c-532f-229e-03312c304217"
    stores = session.get(api_link, headers=headers).json()

    locator_domain = "cemexusa.com"
    found = []

    for store in stores:
        location_name = store["name"].replace("amp;", "")
        street_address = store["address"].replace("amp;", "")
        if location_name == "Cantonment (Dual)" and location_name in found:
            continue
        found.append(location_name)
        city = store["city"]
        state = store["states"]
        zip_code = store["postalCode"]
        country_code = "US"
        store_number = store["id"]

        latitude = store["latitude"]
        longitude = store["longitude"]

        hours_of_operation = store["hours"]
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        location_type = store["product"]
        if not location_type:
            location_type = "<MISSING>"

        try:
            phone = (list(BeautifulSoup(store["phone"], "lxml").stripped_strings))[0]
        except:
            phone = "<MISSING>"

        link = "https://www.cemexusa.com/find-your-location"

        # Store data
        yield [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
