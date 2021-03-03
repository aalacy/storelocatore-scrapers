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

    base_link = "https://api-cdn.storepoint.co/v1/15972423cdba07/locations?rq"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["results"]["locations"]

    data = []
    locator_domain = "pluckers.com"

    for store in stores:
        location_name = store["name"]

        link = store["website"]
        if "http" not in link:
            link = "http://" + link
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        raw_address = list(
            base.find(class_="address-phone w-richtext").stripped_strings
        )
        if ") " in raw_address[0]:
            raw_address = raw_address[2:4]
        street_address = raw_address[0].strip()
        city_line = (
            raw_address[1]
            .replace("TX,", "TX ")
            .replace("Austin TX", "Austin, TX")
            .split(",")
        )
        city = city_line[0]
        state = city_line[1].split()[0].strip()
        zip_code = city_line[1].split()[1].strip()
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = (
            "Monday "
            + store["monday"]
            + " Tuesday "
            + store["tuesday"]
            + " Wednesday "
            + store["wednesday"]
            + " Thursday "
            + store["thursday"]
            + " Friday "
            + store["friday"]
            + " Saturday "
            + store["saturday"]
            + " Sunday "
            + store["sunday"]
        ).strip()
        latitude = store["loc_lat"]
        longitude = store["loc_long"]

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
