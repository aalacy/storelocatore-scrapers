import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("shopbentley_com")


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
    url = "https://www.shopbentley.com/en/storelocator/index/loadstore/"
    r = session.get(url, headers=headers)
    website = "shopbentley.com"
    typ = "<MISSING>"
    country = "CA"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"storelocator_id":"' in line:
            items = line.split('"storelocator_id":"')
            for item in items:
                if "store_name" in item:
                    name = item.split('"store_name":"')[1].split('"')[0]
                    store = item.split('"store_no":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zipcode":"')[1].split('"')[0]
                    hours = (
                        "Sun: "
                        + item.split('"sunday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"sunday_close":"')[1].split('"')[0]
                    )
                    if "0" not in hours:
                        hours = "Sun: Closed"
                    hours = (
                        hours
                        + "; Mon: "
                        + item.split('"monday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"monday_close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + item.split('"tuesday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"tuesday_close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + item.split('"wednesday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"wednesday_close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + item.split('"thursday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"thursday_close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + item.split('"friday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"friday_close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + item.split('"saturday_open":"')[1].split('"')[0]
                        + "-"
                        + item.split('"saturday_close":"')[1].split('"')[0]
                    )
                    if phone == "":
                        phone = "<MISSING>"
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
