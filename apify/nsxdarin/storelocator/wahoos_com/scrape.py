import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("wahoos_com")


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
    url = "https://www.wahoos.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=017a176033&load_all=1&layout=1&category="
    r = session.get(url, headers=headers)
    website = "wahoos.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["id"]
        name = item["title"]
        add = item["street"]
        city = item["city"]
        state = item["state"]
        zc = item["postal_code"]
        lat = item["lat"]
        lng = item["lng"]
        phone = item["phone"]
        cty = item["country"]
        loc = "<MISSING>"
        hours = (
            item["open_hours"]
            .replace('"', "")
            .replace("\\", "")
            .replace("[", "")
            .replace("]", "")
        )
        hours = hours.replace(",", "; ").replace("{", "").replace("}", "")
        if "AM" not in hours and "PM" not in hours:
            hours = "Sun-Sat: Closed"
        if phone == "":
            phone = "<MISSING>"
        if cty == "United States":
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
