import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("relaxtheback_com")


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
    url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=relaxtheback.myshopify.com&latitude=40.7135097&longitude=-73.9859414&max_distance=0&limit=500&calc_distance=1"
    r = session.get(url, headers=headers)
    website = "relaxtheback.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"store_id":"' in line:
            items = line.split('"store_id":"')
            for item in items:
                if '"shop_app_id":' in item:
                    store = item.split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    zc = item.split('"postal_zip":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0].strip()
                    hours = item.split('"hours":"')[1].split('"')[0]
                    hours = hours.replace("\\r\\n", "; ")
                    if hours == "":
                        hours = "<MISSING>"
                    phone = item.split('"phone":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"prov_state":"')[1].split('"')[0]
                    country = item.split('"country":"')[1].split('"')[0]
                    loc = (
                        item.split("Website: <\\/span><a href='")[1]
                        .split("'")[0]
                        .replace("\\", "")
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
