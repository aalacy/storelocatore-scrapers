from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re
import json

DOMAIN = "bssindustrial.co.uk"
SITE_MAP = "https://www.bssindustrial.co.uk/sitemap.xml"
JS_DATA = "https://www.bssindustrial.co.uk/path---branches-e99ca816691bdc2a162f.js"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_page_url(urls, city, location_name):
    for url in urls:
        page_url = url.text
        if (
            city.lower().replace(" ", "-") in page_url
            or location_name.lower().replace(" ", "-") in page_url
        ):
            urls.remove(url)
            return page_url
    return MISSING


def fetch_data():
    log.info("Fetching store_locator data")
    days_key = [
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
    ]
    js = session.get(JS_DATA, headers=HEADERS).text
    soup = pull_content(SITE_MAP)
    page_urls = soup.find_all("loc", text=re.compile(r"\/branches\/\D+.*"))
    data = json.loads(
        re.sub(
            r"([_a-zA-Z]+):",
            r'"\1":',
            re.search(r"edges:(.*)}},pathContext", js)
            .group(1)
            .replace(":.", ":0.")
            .replace(":-.", ":-0.")
            .replace("Main:", "")
            .replace("Out:", ""),
        )
    )
    for row in data:
        row = row["node"]
        location_name = row["title"]
        raw_address = row["address"]
        street_address, city, _, zip_postal = getAddress(raw_address)
        if city == MISSING:
            city = location_name
        if zip_postal == MISSING and city != "Dublin":
            zip_postal = raw_address.split(",")[-1].strip()
        state = MISSING
        phone = row["phone"].split(",")[0].strip()
        country_code = "GB"
        hoo = ""
        for day in days_key:
            time = MISSING if not row[day] else row[day]
            hoo += day.title() + ": " + time + ","
        hours_of_operation = hoo.strip().rstrip(",")
        store_number = MISSING
        location_type = MISSING
        latitude = row["geolocation"]["lat"]
        longitude = row["geolocation"]["lon"]
        page_url = get_page_url(page_urls, city, location_name)
        log.info("Append {} => {}, {}".format(location_name, street_address, city))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
