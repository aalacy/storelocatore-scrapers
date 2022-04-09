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


DOMAIN = "cobsbread.com"
BASE_URL = "https://cobsbread.com"
LOCATION_URL = "https://www.cobsbread.com/local-bakery/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = SgRecord.MISSING


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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    stores = json.loads(
        re.search(
            r"var bakeries = (\[.*\]),?.*",
            soup.find("script", text=re.compile(r"var bakeries.*")).string,
        ).group(1)
    )
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for row in stores:
        page_url = row["link"]
        content = pull_content(page_url)
        location_name = row["title"].replace("&#8211;", "").strip()
        raw_address = row["map_data"]["address"]
        street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            zip
        if "USA" in raw_address:
            country_code = "US"
        elif "Canada" in raw_address:
            country_code = "CA"
        else:
            country_code = raw_address.split(",")[-1].strip()
        store_number = MISSING
        if row["store_status"]:
            location_type = row["store_status"]
        else:
            location_type = MISSING
        phone = MISSING
        try:
            phone = (
                content.find("a", {"class": "single-bakery__phone"})
                .text.replace("\u202c", " ")
                .strip()
            )
        except:
            phone = MISSING
        hoo = ""
        for day in days:
            if "day" in row[day]:
                hoo += row[day] + ", "
            else:
                hoo += day.title() + ": " + row[day] + ", "
        hours_of_operation = hoo.strip().rstrip(",")
        if "Coming Soon" in location_type or "Coming Soon" in location_name:
            location_type = "Coming Soon"
            hours_of_operation = MISSING
        latitude = row["map_data"]["lat"]
        longitude = row["map_data"]["lng"]
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
