import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("schnucks_com")


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
    url = "https://schnucks.locally.com/stores/conversion_data?has_data=true&company_id=136637&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=44.98428912805207&map_center_lng=-93.27137000000019&map_distance_diag=42.597530622701505&sort_by=proximity&no_variants=0&only_retailer_id=136637&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level="
    r = session.get(url, headers=headers)
    website = "schnucks.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["markers"]:
        hours = ""
        store = item["id"]
        name = item["name"]
        lat = item["lat"]
        lng = item["lng"]
        add = item["address"]
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        phone = item["phone"]
        loc = "https://locations.schnucks.com/" + item["slug"]
        days = str(item["display_dow"]).split("{")
        for day in days:
            if "bil_hrs" in day:
                hrs = (
                    day.split("'label': '")[1].split("'")[0]
                    + ": "
                    + day.split("'bil_hrs': '")[1].split("'")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
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
