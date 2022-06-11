import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
import time

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}

logger = SgLogSetup().get_logger("yardhouse_com")


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
    locs = []
    session = SgRequests()
    url = "https://www.yardhouse.com/en-locations-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "yardhouse.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.yardhouse.com/locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        with SgChrome() as driver:
            driver.get(url)
            text = driver.page_source
            text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
            if '"streetAddress":"' in text:
                name = text.split('"name":"')[1].split('"')[0]
                try:
                    hours = (
                        text.split('"openingHours":["')[1]
                        .split('"]')[0]
                        .replace('","', "; ")
                    )
                except:
                    hours = "<MISSING>"
                add = text.split('"streetAddress":"')[1].split('"')[0]
                zc = text.split('"postalCode":"')[1].split('"')[0]
                city = text.split('"addressLocality":"')[1].split('"')[0]
                state = text.split('"addressRegion":"')[1].split('"')[0]
                lat = text.split('"latitude":"')[1].split('"')[0]
                lng = text.split('"longitude":"')[1].split('"')[0]
                store = text.split('"branchCode":"')[1].split('"')[0]
                phone = text.split('"telephone":"')[1].split('"')[0]
        if "kansas-city-downtown-pl-district" in loc:
            add = "1300 Main Street"
            city = "Kansas City"
            state = "MO"
            zc = "64105"
            phone = "(816) 527-0952"
            hours = "Sun-Sat: 11:00AM - 10:00PM"
            store = "8359"
            name = "KANSAS CITY - DOWNTOWN P&L DISTRICT"
        if "san-antonio-the-shops-at-la-cantera" in loc:
            name = "SAN ANTONIO - THE SHOPS AT LA CANTERA"
            add = "15900 La Cantera Parkway  Bldg 23"
            city = "San Antonio"
            state = "TX"
            zc = "78256"
            phone = "(210) 691-0033"
        if zc == "":
            zc = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if state == "":
            state = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if add == "":
            add = "<MISSING>"
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
        time.sleep(60)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
