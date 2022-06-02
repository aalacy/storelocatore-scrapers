from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re


DOMAIN = "scope.org.uk"
BASE_URL = "https://www.scope.org.uk"
LOCATION_URL = "https://www.scope.org.uk/shops/shop-directory/"
API_URL = "https://www.scope.org.uk/api/sitecore/shopsapi/loadmore?id=fbd8e7c8-222f-453f-94a6-114ec0471b4f&page={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    num = 0
    while True:
        data = session.get(API_URL.format(num), headers=HEADERS).json()
        if len(data["results"]) == 0:
            break
        for parent in data["results"]:
            for row in parent:
                location_name = row["title"]
                raw_address = (
                    row["items"][1]["label"]
                    .split("|")[0]
                    .replace("Great Yarmouth,", "")
                    .strip()
                )
                street_address, city, state, zip_postal = getAddress(raw_address)
                if "Unit 2 Theatre Plain" in street_address:
                    city = "Great Yarmouth"
                if zip_postal == MISSING:
                    zip_postal = raw_address.split(",")[-1]
                    street_address = re.sub(
                        zip_postal, "", street_address, flags=re.IGNORECASE
                    ).strip()
                if city == MISSING:
                    city = raw_address.split(",")[1].strip()
                    street_address = re.sub(
                        city + r"\s?", "", street_address, flags=re.IGNORECASE
                    ).strip()
                phone = row["items"][2]["label"].strip()
                country_code = "UK"
                hoo = row["items"][0]["label"]
                if "(Normally open" in hoo:
                    hours_of_operation = re.search(r"(Monday.*)\)", hoo).group(1)
                else:
                    hours_of_operation = (
                        row["items"][0]["label"].replace("Open", "").strip()
                    )
                location_type = row["type"]
                if "Temporarily closed" in hoo:
                    location_type = "TEMP_CLOSED"
                country_code = "UK"
                store_number = MISSING
                latitude = MISSING
                longitude = MISSING
                log.info(
                    f"Append {location_name} => {street_address}, {city}, {zip_postal}"
                )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=LOCATION_URL,
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
        num += 1


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
