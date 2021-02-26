import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("boostmobilelocal_com")


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
    url = "https://boostmobilelocal.com/data/locations.json"
    r = session.get(url, headers=headers)
    website = "boostmobilelocal.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("cp1252").encode("utf-8"))
        if '"title":"' in line:
            items = line.split('"title":"')
            for item in items:
                if '"address":"' in item:
                    name = item.split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0].split("  ")[0]
                    loc = item.split('"url":"')[1].split('"')[0]
                    state = (
                        loc.split("https://boostmobilelocal.com/")[1]
                        .split("/")[0]
                        .upper()
                    )
                    city = loc.split("/")[4].replace("-", " ").title()
                    zc = "<MISSING>"
                    phone = item.split(',"phone":"')[1].split('"')[0]
                    hours = "<MISSING>"
                    store = "<MISSING>"
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
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
