import re
import csv
from random import randint
from time import sleep
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
from concurrent.futures import ThreadPoolExecutor, as_completed

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


driver = SgChrome().driver()


def get_driver(reset=False):
    global driver
    if reset:
        driver = SgChrome().driver()

    return driver


def fetch_location(loc, retry_count=0):
    logger.info(loc)
    website = "thecapitalgrille.com"
    typ = "<MISSING>"
    country = "US"
    CS = False

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

    try:
        with SgChrome(is_headless=True) as driver:
            driver.get(loc)
            sleep(randint(10, 15))

            text = driver.page_source

            if re.search("access denied", re.escape(text), re.IGNORECASE):
                if retry_count > 10:
                    raise Exception()

                return fetch_location(loc, retry_count + 1)

            text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
            if "<title>" in text:
                name = text.split("<title>")[1].split(" |")[0]
            if "> ARRIVING" in text:
                CS = True
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
                lat = "42.562578"
                lng = "-83.18373"
            if "/il/rosemont/chicago-rosemont/8036" in loc:
                name = "Chicago - Rosemont"
                add = "5340 N River Road"
                city = "Chicago"
                state = "IL"
                zc = "60018"
                phone = "(847) 671-8125"
                lat = "41.97486085"
                lng = "-87.86304142"
                hours = "Mon: 4:00PM - 9:00PM; Tue-Thu: 11:00AM - 9:00PM; Fri: 11:30AM - 10:00PM; Sat: 5:00PM - 10:00PM; Sun: 5:00 - 9:00PM"
            if "scottsdale/scottsdale/8024" in loc:
                name = "Scottsdale"
                add = "16489 North Scottsdale Rd"
                city = "Scottsdale"
                state = "AZ"
                zc = "85254"
                phone = "(480) 348-1700"
                lat = "33.63713300"
                lng = "-111.92410500"
                hours = "Mon-Thu: 11:00AM - 9:00PM; Fri: 11:00AM - 10:00PM; Sat: 5:00PM - 10:00PM; Sun: 5:00PM - 9:00PM"
            if "austin/austin/8053" in loc:
                hours = "Mon-Thu: 11:00AM - 9:00PM; Fri: 11:00AM - 10:00PM; Sat: 5:00PM - 10:00PM; Sun: 5:00PM - 9:00PM"
            if "tn/memphis/memphis/8051" in loc:
                hours = "Mon-Thu: 11:30AM - 9:00PM; Fri: 11:30AM - 10:00PM; Sat: 5:00PM - 10:00PM; Sun: 4:00PM - 9:00PM"
            if "/jacksonville/jacksonville/8029" in loc:
                hours = "Mon-Thu: 11:30AM - 9:00PM; Fri: 11:30AM - 10:00PM; Sat: 5:00PM - 10:00PM; Sun: 5:00PM - 9:00PM"
            if "/dunwoody" in loc:
                name = "Atlanta - Dunwoody"
                add = "94 Perimeter Center West"
                city = "Atlanta"
                state = "GA"
                zc = "30346"
                phone = "(770) 730-8447"
                lat = "33.92653800"
                lng = "-84.34037200"
                hours = "Mon-Thu: 11:30AM - 9:00PM; Fri: 11:30AM - 10:00PM; Sat: 5:00PM - 10:00PM; Sun: 4:00PM - 9:00PM"
            if "chevy-chase/8041" in loc:
                city = "Chevy Chase"
                state = "MD"
                add = "5310 Western Ave"
                phone = "(301) 718-7812"
                hours = "Mon-Fri: 11:30AM - 10:00PM; Sat: 12:00PM - 11:00PM; Sun: 4:00PM - 9:00PM"
            if "va/fairfax/fairfax/8068" in loc:
                hours = "Mon-Fri: 11:30AM - 10:00PM; Sat: 5:00PM - 11:00PM; Sun: 5:00PM - 9:00PM"
            if "yndhurst/lyndhurst/8060" in loc:
                hours = "Mon-Thu: 11:30AM - 9:00PM; Fri: 11:30AM - 10:00PM; Sat: 4:00PM - 10:00PM; Sun: 4:00PM - 9:00PM"
            if "charlotte/charlotte/8011" in loc:
                name = "Charlotte"
                phone = "(704) 348-1400"
                zc = "28202"
                add = "201 N. Tryon Street"
                city = "Charlotte"
                state = "NC"
            if "-the-galleria/8007" in loc:
                state = "TX"
                city = "Houston"
                zc = "77056"
                phone = "(713) 623-4600"
                name = "Houston - The Galleria"
                add = "5365 Westheimer Rd"
            if "mc/cuauhtemo" not in loc and "/nl/san-pedro" not in loc:
                if CS:
                    name = name + " - Coming Soon"
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
    except:
        return fetch_location(loc, retry_count + 1)


def fetch_data():
    locs = []
    url = "https://www.thecapitalgrille.com/locations-sitemap.xml"
    r = session.get(url, headers=headers, verify=False)
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://www.thecapitalgrille.com/locations/" in line
            and "/mexico/" not in line
        ):
            locs.append(line.split("<loc>")[1].split("<")[0])

    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(fetch_location, loc) for loc in locs]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
