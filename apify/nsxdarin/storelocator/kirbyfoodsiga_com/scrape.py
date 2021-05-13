import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("kirbyfoodsiga_com")


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
    url = "https://api.freshop.com/1/stores?app_key=kirby_foods_iga&has_address=true&is_selectable=true&limit=50&token=57701bf01e371bcec77bec3b61bfc444"
    r = session.get(url, headers=headers)
    website = "kirbyfoodsiga.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["items"]:
        store = item["id"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["name"]
        loc = item["url"]
        add = item["address_1"]
        city = item["city"]
        state = item["state"]
        zc = item["postal_code"]
        hours = item["hours_md"]
        phone = item["phone"]
        phone = str(phone)
        phone = (
            phone.replace("\n", "").replace("\r", "").replace("\t", "").replace("*", "")
        )
        hours = str(hours)
        hours = (
            hours.replace("\n", "").replace("\r", "").replace("\t", "").replace("*", "")
        )
        if "Pharmacy" in hours:
            hours = hours.split("Pharmacy")[0].strip()
        if "Fax" in phone:
            phone = phone.split("Fax")[0].strip()
        if "Pharmacy" in phone:
            phone = phone.split("Pharmacy")[0].strip()
        phone = phone.replace("Store: ", "")
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
