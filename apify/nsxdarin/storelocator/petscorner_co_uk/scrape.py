import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("petscorner_co_uk")


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
    url = "https://www.petscorner.co.uk/storefinder/index/loadstore/?websiteIds[]=1"
    r = session.get(url, headers=headers)
    website = "petscorner.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["stores"]:
        store = item["store_id"]
        hours = ""
        name = item["name"]
        loc = "https://www.petscorner.co.uk/" + item["slug"]
        lat = item["latitude"]
        lng = item["longitude"]
        add = item["address_line_1"]
        try:
            add = add + " " + item["address_line_2"]
        except:
            pass
        city = item["city"]
        state = item["county"]
        zc = item["postcode"]
        phone = item["phone"]
        for day in item["opening_times"]["regular"]:
            hrs = day["name"] + ": " + day["time_open"] + "-" + day["time_close"]
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        if state is None or state == "":
            state = "<MISSING>"
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
