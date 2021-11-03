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

    base_link = "https://dealersearch.audi.com/api/json/v2/audi-usa/show_all"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["partners"]

    data = []
    locator_domain = "audiusa.com"

    for store in stores:
        location_name = store["name"]
        street_address = store["address"]["display"][0].split(",")[0].strip()
        city = store["address"]["city"]
        state = store["address"]["region"]
        zip_code = store["address"]["zipCode"]
        country_code = store["countryCode"]
        store_number = store["vendorId"]
        location_type = "<MISSING>"
        phone = store["contactDetails"]["phone"]["display"]
        hours_of_operation = BeautifulSoup(
            store["notes"]["openingHoursHTML"], "lxml"
        ).getText(" ")
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]
        link = "https://www.audiusa.com/us/web/en/shopping-tools/dealer-search.html"

        # Store data
        data.append(
            [
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
