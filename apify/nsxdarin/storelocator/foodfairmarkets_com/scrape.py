import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("foodfairmarkets_com")


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
    url = "https://api.freshop.com/1/stores?app_key=foodfair_market&has_address=true&limit=-1&token=c72377d6afbdea7fdebdf15fb0eedfb6"
    r = session.get(url, headers=headers)
    website = "foodfairmarkets.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["items"]:
        store = item["id"]
        name = item["name"]
        lat = item["latitude"]
        lng = item["longitude"]
        loc = item["url"]
        add = item["address_1"]
        city = item["city"]
        try:
            state = item["state"]
        except:
            state = "<MISSING>"
        zc = item["postal_code"]
        hours = item["hours_md"]
        phone = item["phone_md"]
        if city == "Ironton":
            state = "OH"
        if city == "West Hamlin":
            state = "WV"
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
