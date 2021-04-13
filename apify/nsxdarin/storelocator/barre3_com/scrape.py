import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("barre3_com")


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
    url = "https://storerocket.global.ssl.fastly.net/api/user/jN49m3n4Gy/locations"
    r = session.get(url, headers=headers)
    website = "barre3.com"
    typ = "<MISSING>"
    hours = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["results"]["locations"]:
        store = item["id"]
        loc = "https://barre3.com/studio-locations/" + item["slug"]
        add = item["address_line_1"]
        try:
            add = add + " " + item["address_line_2"]
        except:
            pass
        city = item["city"]
        state = item["state"]
        zc = item["postcode"]
        phone = item["phone"]
        lat = item["lat"]
        lng = item["lng"]
        name = item["name"]
        if "939-2510" in str(phone):
            phone = "480-939-2510"
        if "811.2828" in str(phone):
            phone = "811.2828"
        if phone is None:
            phone = "<MISSING>"
        if "R3 Level," in str(add):
            add = "R3 Level, Power Plant Mall, Rockwell Center"
        if state != "":
            if zc != "":
                if add == "":
                    add = "<MISSING>"
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
