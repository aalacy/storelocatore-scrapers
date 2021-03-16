import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("thecapitalgrille_com")


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
    url = "https://www.thecapitalgrille.com/locations-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "thecapitalgrille.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://www.thecapitalgrille.com/locations/" in line
            and "/mexico/" not in line
        ):
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        time.sleep(10)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        with SgChrome() as driver:
            driver.get(url)
            text = driver.page_source
            text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
            if "<title>" in text:
                name = text.split("<title>")[1].split(" |")[0]
            if '"postalCode":"' in text:
                zc = text.split('"postalCode":"')[1].split('"')[0]
            if '"addressRegion":"' in text:
                state = text.split('"addressRegion":"')[1].split('"')[0]
            if '"streetAddress":"' in text:
                add = text.split('"streetAddress":"')[1].split('"')[0]
                phone = text.split('telephone":"')[1].split('"')[0]
            if '"addressRegion":"' in text:
                city = text.split('addressLocality":"')[1].split('"')[0]
            if '"latitude":"' in text:
                lat = text.split('"latitude":"')[1].split('"')[0]
                lng = text.split('"longitude":"')[1].split('"')[0]
            if ',"openingHours":["' in text:
                hours = (
                    text.split(',"openingHours":["')[1]
                    .split('"]')[0]
                    .replace('","', "; ")
                )
        if hours == "":
            hours = "<MISSING>"
        if "/troy/" in loc:
            name = "Troy"
            add = "2800 West Big Beaver Rd"
            city = "Troy"
            state = "MI"
            zc = "48084"
            phone = "(248) 649-5300"
            lat = "<MISSING>"
            lng = "<MISSING>"
        if "mc/cuauhtemo" not in loc and "/nl/san-pedro" not in loc:
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
