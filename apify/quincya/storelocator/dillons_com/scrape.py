import csv
import json

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

    base_link = "https://www.dillons.com/storelocator-sitemap.xml"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("loc")

    data = []
    locator_domain = "dillons.com"

    for item in items:
        link = item.text
        if "stores/details" in link:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                script = (
                    base.find("script", attrs={"type": "application/ld+json"})
                    .text.replace("\n", "")
                    .strip()
                )
            except:
                continue
            store = json.loads(script)

            location_name = store["name"]

            try:
                street_address = store["address"]["streetAddress"]
                city = store["address"]["addressLocality"]
                state = store["address"]["addressRegion"]
                zip_code = store["address"]["postalCode"]
            except:
                raw_address = (
                    base.find(class_="StoreAddress-storeAddressGuts")
                    .get_text(" ")
                    .replace(",", "")
                    .replace(" .", ".")
                    .split("  ")
                )
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = raw_address[2].strip()
                zip_code = raw_address[3].split("Get")[0].strip()

            country_code = "US"
            store_number = link.split("/")[-1]
            location_type = "<MISSING>"
            phone = store["telephone"]
            if not phone:
                phone = "<MISSING>"
            hours_of_operation = store["openingHours"][0]
            latitude = store["geo"]["latitude"]
            longitude = store["geo"]["longitude"]

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
