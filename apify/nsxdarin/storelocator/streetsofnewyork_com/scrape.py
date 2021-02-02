import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}

logger = SgLogSetup().get_logger("streetsofnewyork_com")


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
    ids = []
    url = "https://www.streetsofnewyork.com/locations"
    r = session.get(url, headers=headers)
    website = "streetsofnewyork.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"isStripePaymentAvailable":false,"lat":' in line:
            items = line.split('"isStripePaymentAvailable":false,"lat":')
            for item in items:
                if '"menuLandingPageUrl":' in item:
                    lat = item.split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
                    name = (
                        item.split('"name":"')[1].split('"')[0].replace("\\u0026", "&")
                    )
                    phone = item.split('"phone":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    store = item.split('"restaurantId":"')[1].split('"')[0]
                    hours = (
                        item.split('"schemaHours":["')[1]
                        .split('"],')[0]
                        .replace('","', "; ")
                    )
                    state = item.split('"state":"')[1].split('"')[0]
                    add = item.split(',"streetAddress":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    if add not in ids:
                        ids.append(add)
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
