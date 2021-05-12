import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = SgLogSetup().get_logger("pacsun.com")


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

    session = SgRequests()

    base_link = "https://www.pacsun.com/stores"

    headers = {
        "authority": "www.pacsun.com",
        "method": "POST",
        "path": "/stores",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "100",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.pacsun.com",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
    )
    log.info("Running sgzips ..")

    found = []
    for zip_code in search:

        payload = {"postalCode": zip_code}
        response = session.post(base_link, headers=headers, data=payload)
        base = BeautifulSoup(response.text, "lxml")

        locator_domain = "pacsun.com"

        stores = base.find_all(class_="sl-store")

        if len(stores) > 0:
            all_scripts = base.find_all("script")
            for script in all_scripts:
                if "storeList = " in str(script):
                    store_json = json.loads(
                        str(script).split("=")[1].split("var slS")[0]
                    )
                    break

            for store in stores:
                location_name = store.h2.text.strip()
                if "CLOSED" in location_name.upper():
                    continue

                link = "https://www.pacsun.com/stores"

                phone = store.find(class_="phone-number").text.strip()

                street_address = store.find(
                    class_="address-phone-info"
                ).div.text.strip()
                city_line = (
                    store.find(class_="address-phone-info")
                    .find_all("div")[1]
                    .text.strip()
                    .replace("\t", "")
                    .split("\n")
                )
                city = city_line[0].replace(",", "")
                state = city_line[1]
                zip_code = city_line[2]
                country_code = "US"
                store_number = store["id"]
                if store_number in found:
                    continue
                found.append(store_number)
                location_type = "<MISSING>"

                hours_of_operation = (
                    store.find(class_="storehours").get_text(" ").strip()
                )
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                for j in store_json:
                    if j["ID"] == store_number:
                        latitude = j["lat"]
                        longitude = j["long"]
                        search.found_location_at(latitude, longitude)
                        break

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
