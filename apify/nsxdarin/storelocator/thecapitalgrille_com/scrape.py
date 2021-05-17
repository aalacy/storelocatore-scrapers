import re
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
from tenacity import retry, stop_after_attempt
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


@retry(reraise=True, stop=stop_after_attempt(3))
def fetch(loc, driver):
    return driver.execute_async_script(
        f"""
        var done = arguments[0]

        fetch("{loc}")
            .then(res => res.text())
            .then(done)
    """
    )


@retry(reraise=True, stop=stop_after_attempt(3))
def fetch_location(loc, driver):
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
    text = fetch(loc, driver)

    if re.search("access denied", text, re.IGNORECASE):
        raise Exception()

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
        hours = text.split(',"openingHours":["')[1].split('"]')[0].replace('","', "; ")

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

    with ThreadPoolExecutor() as executor, SgChrome() as driver:
        driver.get("https://www.thecapitalgrille.com/home")
        futures = [executor.submit(fetch_location, loc, driver) for loc in locs]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
