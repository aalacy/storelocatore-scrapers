import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hrblock_ca")


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
    url = "https://www.hrblock.ca/assets/data/office-locator/index.json"
    r = session.get(url, headers=headers)
    website = "hrblock.ca"
    typ = "<MISSING>"
    country = "CA"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["data"]["craft"]["officeLocations"]:
        store = item["Office_ID"]
        add = item["Address"]
        city = item["City"]
        state = item["Province"]
        zc = item["Postal_Code"]
        hours = item["Opening_Hours"]
        phone = item["phone_number"]
        lat = item["lat"]
        lng = item["lng"]
        loc = "https://www.hrblock.ca/stores/" + add.replace("#", "").replace(" ", "-")
        typ = str(item["Type"])
        if " - " in typ:
            typ = typ.split(" - ")[0]
        name = "H&R Block #" + str(store)
        if hours == "" or hours is None:
            hours = "<MISSING>"
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
