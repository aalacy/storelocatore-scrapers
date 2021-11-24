import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://bonchon.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="locations-list-item")

    for item in items:

        locator_domain = "bonchon.com"
        location_name = item["data-location-name"]

        raw_address = list(item.address.stripped_strings)
        street_address = raw_address[0].strip()
        city_line = raw_address[-1].strip().replace("\n", "").split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip()[:-5].strip()
        zip_code = city_line[-1][-5:].strip()
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        country_code = "US"
        store_number = item["data-id"]
        phone = item.find(class_="locations-list-item__tel").text.strip()
        if not phone:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = item["data-latitude"]
        longitude = item["data-longitude"]

        link = item.find(class_="locations-list-item__menu-link")["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "coming soon" in base.find(class_="location__inner").text.lower():
            continue

        hours_of_operation = (
            " ".join(list(base.find(class_="location__hours").stripped_strings))
            .replace("\n", " ")
            .replace("  ", "")
            .strip()
        )

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
