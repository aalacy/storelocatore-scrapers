import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("marcos_com")


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
    url = "https://www.marcos.com/api/stores/getAllStore?listStores=true"
    r = session.get(url, headers=headers)
    website = "marcos.com"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["results"]:
        store = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        try:
            loc = item["baseUrl"].replace("\\", "")
        except:
            loc = "<MISSING>"
        name = item["name"]
        add = item["address"]
        try:
            phone = item["telephone"]
        except:
            phone = "<MISSING>"
        try:
            zc = item["zip"]
        except:
            zc = "<MISSING>"
        try:
            state = item["state"]
        except:
            state = "<MISSING>"
        try:
            city = item["city"]
        except:
            city = "<MISSING>"
        lat = item["lat"]
        lng = item["lng"]
        if " - " in name:
            store = name.split(" - ")[0]
        if state != "BH" and "Bahamas" not in name and "Bahamas" not in add:
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
