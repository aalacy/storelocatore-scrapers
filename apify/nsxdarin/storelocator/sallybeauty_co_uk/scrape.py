import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("sallybeauty_co_uk")


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
    url = "https://www.sallybeauty.co.uk/on/demandware.store/Sites-sally-beauty-Site/en_GB/Stores-GetStoresJSON"
    r = session.get(url, headers=headers)
    website = "sallybeauty.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["ID"]
        state = "<MISSING>"
        name = item["name"]
        add = item["address"]
        phone = item["phone"]
        city = item["city"]
        zc = item["postalCode"]
        lat = item["latitude"]
        lng = item["longitude"]
        hours = item["hours"]
        loc = "https://www.sallybeauty.co.uk/storeinfo?StoreID=" + store
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if hours == "" or hours is None:
            hours = "<MISSING>"
        addinfo = item["formattedAddress"]
        if addinfo.count(",") == 4:
            add = addinfo.split(",")[0] + " " + addinfo.split(",")[1]
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
