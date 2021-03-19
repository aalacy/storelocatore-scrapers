import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("wowbao_com")


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
    url = "https://api2.storepoint.co/v1/15fe0bd667ae7b/locations?lat=33.7225&long=-116.377&radius=5000"
    r = session.get(url, headers=headers)
    website = "wowbao.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["results"]["locations"]:
        store = item["id"]
        lat = item["loc_lat"]
        lng = item["loc_long"]
        name = item["name"]
        addinfo = item["streetaddress"]
        add = "<MISSING>"
        city = addinfo.split(",")[0]
        state = addinfo.split(",")[1].strip()
        zc = "<MISSING>"
        phone = "<MISSING>"
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
