import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("whistles_com")


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
    url = "https://www.whistles.com/on/demandware.store/Sites-WH-US-Site/en_US/Stores-FindStores?lat=51.378051&long=-3.435973&dwfrm_address_country=US&postalCode="
    r = session.get(url, headers=headers)
    website = "whistles.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["stores"]:
        store = item["ID"]
        name = item["name"]
        add = item["address1"]
        try:
            add = add + " " + item["address2"]
        except:
            pass
        state = "<MISSING>"
        city = item["city"]
        zc = item["postalCode"]
        lat = item["latitude"]
        lng = item["longitude"]
        phone = item["phone"]
        typ = item["storeType"]
        hours = ""
        for day in item["workTimes"]:
            hrs = day["weekDay"] + ": " + day["value"]
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        loc = "https://www.whistles.com/us/stores/details?storeID=" + store
        if "Shepton Mallet" in add:
            city = "Shepton Mallet"
            add = add.replace("Shepton Mallet", "").strip()
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
