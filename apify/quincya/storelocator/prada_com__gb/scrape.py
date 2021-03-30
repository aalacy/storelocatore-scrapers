import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="prada.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://www.prada.com/gb/en.nux.getAllStores.json"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()

    data = []

    locator_domain = "prada.com"

    for i in store_data:
        if not i[0].isupper():
            continue
        items = store_data[i]
        for item in items:
            try:
                country_code = item["country"]
            except:
                continue
            if country_code != "GB":
                continue
            link = "https://www.prada.com/gb/en/store-locator" + item["url"]
            log.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            js = base.find(id="jsonldLocalBusiness").text
            try:
                store = json.loads(js)
            except:
                continue

            country_code = store["address"]["addressCountry"]
            location_name = store["name"].strip()
            street_address = store["address"]["streetAddress"].strip()
            city = store["address"]["addressLocality"]
            state = "<MISSING>"
            zip_code = store["address"]["postalCode"]
            store_number = link.split(".")[-2]
            location_type = "<MISSING>"
            phone = store["telephone"].strip()
            hours_of_operation = (
                store["openingHours"].strip().replace("  ", " ").replace("--", "Closed")
            )
            latitude = store["geo"]["latitude"]
            longitude = store["geo"]["longitude"]

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
