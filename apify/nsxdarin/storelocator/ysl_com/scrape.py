import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ysl_com")


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
    ccodes = ["US", "GB", "CA"]
    website = "ysl.com"
    typ = "<MISSING>"
    for ccode in ccodes:
        url = (
            "https://www.ysl.com/on/demandware.store/Sites-SLP-NOAM-Site/en_US/Stores-FindStoresData?countryCode="
            + ccode
        )
        r = session.get(url, headers=headers)
        country = ccode
        logger.info("Pulling Stores")
        for item in json.loads(r.content)["storesData"]["stores"]:
            store = item["ID"]
            name = item["name"]
            add = item["address1"]
            city = item["city"]
            zc = item["postalCode"]
            state = item["stateCode"]
            phone = item["phone"]
            lat = item["latitude"]
            lng = item["longitude"]
            loc = item["detailsUrl"]
            hours = item["storeHours"].replace("\n", "")
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
