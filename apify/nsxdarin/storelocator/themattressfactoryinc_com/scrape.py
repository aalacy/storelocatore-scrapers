import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("themattressfactoryinc_com")


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
    url = "https://www.themattressfactoryinc.com/get-mattress-store-all/"
    r = session.get(url, headers=headers)
    website = "themattressfactoryinc.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["mattressStoreID"]
        name = item["title"]
        add = item["address"]
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        phone = item["phone"]
        lat = item["latitude"]
        lng = item["longitude"]
        try:
            hours = (
                "Mon-Fri: "
                + item["regHours"]
                + "; Sat: "
                + item["satHours"]
                + "; Sun: "
                + item["sunHours"]
            )
        except:
            hours = "<MISSING>"
        if "Tues, Wed, Thurs" in hours:
            hours = hours.replace("Mon-Fri", "Mon, Fri")
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
