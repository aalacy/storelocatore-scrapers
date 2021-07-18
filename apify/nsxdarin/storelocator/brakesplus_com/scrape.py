import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("brakesplus_com")


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
    url = "https://www.brakesplus.com/stores/"
    r = session.get(url, headers=headers)
    website = "brakesplus.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "var m247Retailers" in line:
            items = line.split('"location":')
            for item in items:
                if '"storenum":"' in item:
                    store = item.split('"storenum":"')[1].split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
                    loc = (
                        "https://www.brakesplus.com"
                        + item.split('"link":"')[1].split('"')[0]
                    )
                    phone = item.split('"ph":"')[1].split('"')[0]
                    add = item.split('"addr1":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    hours = "Sun: " + item.split('"Sun":"')[1].split('"')[0]
                    hours = hours + "; Mon: " + item.split('"Mon":"')[1].split('"')[0]
                    hours = hours + "; Tue: " + item.split('"Tue":"')[1].split('"')[0]
                    hours = hours + "; Wed: " + item.split('"Wed":"')[1].split('"')[0]
                    hours = hours + "; Thu: " + item.split('"Thu":"')[1].split('"')[0]
                    hours = hours + "; Fri: " + item.split('"Fri":"')[1].split('"')[0]
                    hours = hours + "; Sat: " + item.split('"Sat":"')[1].split('"')[0]
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
