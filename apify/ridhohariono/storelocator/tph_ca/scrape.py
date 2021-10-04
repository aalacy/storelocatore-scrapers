import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "tph.ca"
BASE_URL = "https://tph.ca/"
LOCATION_URL = "https://www.tph.ca/printing-near-me"
API_URL = "https://www.tph.ca/wp-content/uploads/agile-store-locator/locator-data.json?v=1&action=asl_load_stores&load_all=1&layout=1"
SINGLE_STORE = "https://www.tph.ca/myaccount/API/Branch/BranchesByBranchNo?ID={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


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


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)!3d([\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def get_json_content(soup):
    try:
        content = soup.find("script", {"type": "application/ld+json"}).string.replace(
            "\n", ""
        )
    except:
        return False
    return json.loads(content)


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        store_number = row["title"]
        page_url = row["website"]
        info = session.get(SINGLE_STORE.format(store_number), headers=HEADERS).json()
        location_name = info["Name"]
        if "CLOSED" in location_name.upper():
            continue
        street_address = row["street"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["postal_code"]
        phone = row["phone"]
        country_code = "CA"
        location_type = "The Printing House"
        latitude = row["lat"]
        longitude = row["lng"]
        if info["HoursFri"] == info["HoursMToT"]:
            hoo = "Mon - Fri: " + info["HoursFri"]
        else:
            hoo = hoo = "Mon: " + info["HoursMToT"] + ", Fri:" + info["HoursFri"]
        hours_of_operation = (
            hoo + ", Sat:" + info["HoursSat"] + ", Sun:" + info["HoursSun"]
        )
        log.info("Append {} => {}".format(location_name, street_address))
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
