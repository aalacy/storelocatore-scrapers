# coding=UTF-8

import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("highsstores_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    session = SgRequests()

    addresses = []

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    base_url = "https://www.highs.com/"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        max_radius_miles=50,
        max_search_results=100,
    )
    logger.info("Running Sgzip ..")
    for lat, lng in search:
        location_url = (
            "https://www.highs.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results=25&search_radius=50&autoload=1"
        )
        try:
            json_data = session.get(location_url, headers=headers).json()
        except:
            session = SgRequests()
            continue
        for i in json_data:
            location_name = i["store"].replace("&#8217;", "’").replace("&#8211;", "-")
            street_address = i["address"]
            city = i["city"]
            state = i["state"]
            zipp = i["zip"]
            store_number = i["id"]
            phone = i["phone"]
            if not phone:
                phone = "<MISSING>"
            latitude = i["lat"]
            longitude = i["lng"]
            search.found_location_at(latitude, longitude)
            table_data = [
                [cell.text for cell in row("td")]
                for row in BeautifulSoup(i["hours"], features="lxml")("tr")
            ]
            hours_of_operation = (
                json.dumps(dict(table_data))
                .replace("{", "")
                .replace("}", "")
                .replace('"', "")
                .replace(",", "")
            )
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append("https://www.highs.com/locations/")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
