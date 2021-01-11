import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("schnucks_com")


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
    url = "https://locations.schnucks.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "schnucks.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://locations.schnucks.com/" in line:
            items = line.split("<loc>https://locations.schnucks.com/")
            for item in items:
                if "<?xml" not in item:
                    locs.append("https://locations.schnucks.com/" + item.split("<")[0])
    for loc in locs:
        logger.info(loc)
        time.sleep(3)
        name = ""
        add = ""
        city = ""
        state = loc.split(".com/")[1].split("-")[0].upper()
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split(" |")[0]
            if '"branchCode":"' in line2:
                store = line2.split('"branchCode":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0].strip()
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                phone = (
                    line2.split('"telephone":"')[1]
                    .split('"')[0]
                    .replace("+", "")
                    .strip()
                )
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
                days = line2.split('"dayOfWeek":"')
                for day in days:
                    if '"opens":"' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"opens":"')[1].split('"')[0]
                            + "-"
                            + day.split('"closes":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
