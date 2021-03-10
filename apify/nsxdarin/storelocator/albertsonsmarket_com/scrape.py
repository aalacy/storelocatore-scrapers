import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("albertsonsmarket_com")


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
    ids = []
    url = "https://www.albertsonsmarket.com/RS.Relationshop/StoreLocation/GetAllStoresPosition"
    r = session.get(url, headers=headers)
    website = "albertsonsmarket.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["StoreID"]
        loc = "https://www.albertsonsmarket.com/rs/StoreLocator?id=" + str(store)
        add = item["Address1"]
        city = item["City"]
        lat = item["Latitude"]
        lng = item["Longitude"]
        phone = item["PhoneNumber"]
        state = item["State"]
        hours = item["StoreHours"]
        zc = item["Zipcode"]
        name = item["StoreName"]
        if store not in ids:
            ids.append(store)
            yield [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
