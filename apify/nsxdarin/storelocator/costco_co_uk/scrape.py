import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("costco_co_uk")


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
    url = "https://www.costco.co.uk/store-finder/search?q=United+Kingdom&page=0"
    r = session.get(url, headers=headers)
    website = "costco.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["data"]:
        name = item["displayName"]
        loc = "<MISSING>"
        add = item["line1"] + " " + item["line2"]
        add = add.strip()
        phone = item["phone"]
        state = "<MISSING>"
        city = item["town"]
        lat = item["latitude"]
        lng = item["longitude"]
        hours = "Sun: " + item["openings"]["Sun"]["individual"]
        hours = hours + "; Mon: " + item["openings"]["Mon"]["individual"]
        hours = hours + "; Tue: " + item["openings"]["Tue"]["individual"]
        hours = hours + "; Wed: " + item["openings"]["Wed"]["individual"]
        hours = hours + "; Thu: " + item["openings"]["Thu"]["individual"]
        hours = hours + "; Fri: " + item["openings"]["Fri"]["individual"]
        hours = hours + "; Sat: " + item["openings"]["Sat"]["individual"]
        zc = item["postalCode"]
        store = "<MISSING>"
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
