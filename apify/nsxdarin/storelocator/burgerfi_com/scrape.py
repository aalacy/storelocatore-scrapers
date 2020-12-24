import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("burgerfi_com")


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
    url = "https://order.burgerfi.com/api/restaurants"
    r = session.get(url, headers=headers)
    website = "burgerfi.com"
    typ = "<MISSING>"
    country = "US"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"acceptsordersbeforeopening":' in line:
            items = line.split('{"acceptsordersbeforeopening":')
            for item in items:
                if 'isavailable":' in item and "Corporate Office" not in item:
                    store = item.split('"id":')[1].split(",")[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    add = item.split('"streetaddress":"')[1].split('"')[0]
                    phone = item.split('"telephone":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    try:
                        city = item.split('"city":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    state = item.split('"state":"')[1].split('"')[0]
                    loc = (
                        "https://order.burgerfi.com/locations/"
                        + state
                        + "/"
                        + city
                        + "/"
                        + store
                    )
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    if "15201 Potomac" in add:
                        city = "Woodbridge"
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
