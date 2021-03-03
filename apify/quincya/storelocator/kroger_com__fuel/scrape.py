import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("kroger.com")


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

    base_link = "https://www.kroger.com/storelocator-sitemap.xml"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all("loc")

    data = []
    locator_domain = "kroger.com"

    log.info("Processing " + str(len(items)) + " links ...")
    for i, item in enumerate(items):
        link = item.text
        if "stores/details" in link:

            # New session every 20
            if i % 20 == 0:
                if i > 0:
                    log.info("Getting next 20 ..")
                    log.info(link)
                    session = SgRequests()

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                if (
                    "gas"
                    not in base.find(class_="StoreServices-wrapper table").text.lower()
                ):
                    continue
            except:
                continue

            try:
                script = (
                    base.find("script", attrs={"type": "application/ld+json"})
                    .text.replace("\n", "")
                    .strip()
                )
            except:
                log.info(link)
                raise
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
                    .replace("8  Rd", "8 Rd")
                    .replace(" .", ".")
                    .replace("..", ".")
                    .split("  ")
                )
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = raw_address[2].strip()
                zip_code = raw_address[3].split("Get")[0].strip()

            country_code = "US"
            store_number = "/".join(link.split("/")[-2:])
            location_type = "<MISSING>"
            try:
                phone = store["telephone"]
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"

            hours_of_operation = ""
            raw_hours = store["openingHours"]
            for hours in raw_hours:
                hours_of_operation = (hours_of_operation + " " + hours).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

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
