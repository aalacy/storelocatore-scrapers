import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("pizzamyheart_com")


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
    url = "https://www.pizzamyheart.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "pizzamyheart.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"name": "' in line:
            items = line.split('{"name": "')
            for item in items:
                if '"slug": "' in item:
                    loc = (
                        "https://www.pizzamyheart.com"
                        + item.split('"url": "')[1].split('"')[0]
                    )
                    name = item.split('"')[0]
                    hours = item.split('"hours": "\\u003cp\\u003e')[1].split(
                        "\\u003c/p\\u003e\\u003cp\\u003e\\u003ca class"
                    )[0]
                    hours = hours.replace("\\u003c/p\\u003e\\u003cp\\u003e", "; ")
                    add = item.split('"street": "')[1].split('"')[0]
                    city = item.split('"city": "')[1].split('"')[0]
                    state = item.split('"state": "')[1].split('"')[0]
                    zc = item.split('"postal_code": "')[1].split('"')[0]
                    lat = item.split('"lat": "')[1].split('"')[0]
                    lng = item.split('"lng": "')[1].split('"')[0]
                    phone = item.split('"phone_number": "')[1].split('"')[0]
                    store = "<MISSING>"
                    hours = hours.replace("\\u0026amp;", "&")
                    hours = hours.replace("\\u0026nbsp;", "")
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
