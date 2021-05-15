import csv
import time
import random
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("longhornsteakhouse_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authority": "www.longhornsteakhouse.com",
    "scheme": "https",
    "cache-control": "max-age=0",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "method": "GET",
}


def sleep():
    time.sleep(random.randint(4, 7))


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


@retry(stop=stop_after_attempt(3))
def fetch_location(loc):
    with SgChrome(executable_path="/bin/chromedriver") as driver:
        logger.info("Pulling Location %s..." % loc)
        website = "longhornsteakhouse.com"
        typ = "Restaurant"
        hours = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        country = ""
        name = ""
        store = loc.rsplit("/", 1)[1]

        driver.get(loc)
        text = driver.page_source
        text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
        if 'id="restLatLong" value="' in text:
            lat = text.split('id="restLatLong" value="')[1].split(",")[0]
            lng = text.split('id="restLatLong" value="')[1].split(",")[1].split('"')[0]
        if '"weekda' in text:
            day = text.split('"weekda')[1].split('">')[1].split("<")[0]
            if "(" in day:
                day = day.split("(")[1].split(")")[0]
        if "<title>" in text:
            name = text.split("<title>")[1].split(" |")[0]
        if 'id="restAddress" value="' in text:
            add = text.split('id="restAddress" value="')[1].split(",")[0]
            city = text.split('id="restAddress" value="')[1].split(",")[1]
            state = text.split('id="restAddress" value="')[1].split(",")[2]
            zc = text.split('id="restAddress" value="')[1].split(",")[3].split('"')[0]
            country = "US"
        if '"streetAddress":"' in text:
            if add == "":
                add = text.split('"streetAddress":"')[1].split('"')[0]
                country = text.split('"addressCountry":"')[1].split('"')[0]
                city = text.split('"addressLocality":"')[1].split('"')[0]
                state = text.split('"addressRegion":"')[1].split('"')[0]
                zc = text.split('"postalCode":"')[1].split('"')[0]
            if lat == "":
                try:
                    lat = text.split('"latitude":"')[1].split('"')[0]
                    lng = text.split('"longitude":"')[1].split('"')[0]
                except:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
        if '"openingHours":["' in text:
            hours = (
                text.split('"openingHours":["')[1].split('"]')[0].replace('","', "; ")
            )
        if ',"telephone":"' in text:
            phone = text.split(',"telephone":"')[1].split('"')[0]

        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "Cincinnati - Eastgate" in name:
            phone = "(513) 947-8882"
        if "Orchard Park" in name:
            phone = "(716) 825-1378"
        if "Gainesville" in name:
            phone = "(352) 372-5715"
        if "Find A R" not in name:
            return [
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


def fetch_data():
    locs = []
    url = "https://www.longhornsteakhouse.com/locations-sitemap.xml"
    session = SgRequests()
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.longhornsteakhouse.com/locations/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_location, loc) for loc in locs]
        for future in as_completed(futures):
            yield future.result()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
