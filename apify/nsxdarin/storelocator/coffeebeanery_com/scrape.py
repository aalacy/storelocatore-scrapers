import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("coffeebeanery_com")


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
    url = "https://cdn.shopify.com/s/files/1/0069/1719/3781/t/102/assets/sca.storelocatordata.json?v=1613366058&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    r = session.get(url, headers=headers)
    website = "coffeebeanery.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        lat = item["lat"]
        lng = item["lng"]
        name = item["name"]
        try:
            phone = item["phone"]
        except:
            phone = "<MISSING>"
        loc = "https://www.coffeebeanery.com/pages/store-locator"
        try:
            hours = (
                item["schedule"]
                .replace("<br>", "; ")
                .replace("\\r", "")
                .replace("|", ":")
            )
        except:
            hours = "<MISSING>"
        add = item["address"]
        city = item["city"]
        state = item["state"]
        try:
            zc = item["postal"]
        except:
            zc = "<MISSING>"
        store = item["id"]
        if item["country"] == "Guam":
            state = "Guam"
        hours = hours.replace("\r", "").replace(" :", ":")
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
