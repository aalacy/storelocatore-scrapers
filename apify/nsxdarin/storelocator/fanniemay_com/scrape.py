import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "s": "jz2bduhpAnk3kRAD6tOTOA0UY+OsQ4+Bug2RUBdjV/U=",
}

logger = SgLogSetup().get_logger("fanniemay_com")


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
    url = "https://www.fanniemay.com/ajax/location/getAllLocations/"
    payload = {"locations": [[41.742326, -87.9304181]], "all": "y"}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "fanniemay.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Id":' in line:
            items = line.split('"Id":')
            for item in items:
                if '"Features"' in item:
                    store = item.split(",")[0]
                    loc = "<MISSING>"
                    name = item.split('"Name":"')[1].split('"')[0]
                    add = item.split('"Address":"')[1].split('"')[0]
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"State":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    lat = item.split('"Lat":"')[1].split('"')[0]
                    lng = item.split('"Lng":"')[1].split('"')[0]
                    hours = (
                        item.split('"HoursMessage":"')[1]
                        .split('"')[0]
                        .replace("<br />", "; ")
                    )
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
