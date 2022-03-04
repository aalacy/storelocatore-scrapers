from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "frame-store.com"
LOCATION_URL = "https://frame-store.com/pages/stores"
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.stores-list__grid--all div.stores-list__store")
    latlong_content = soup.find("script", string=re.compile(r"SDG\.Data\.stores"))
    latlong = re.findall(r"store\['latLng'\] = '(.*)';", latlong_content.string)
    num = 0
    for row in contents:
        page_url = (
            LOCATION_URL
            + "?location="
            + row.find("button", {"class": "stores-list__store-title"})[
                "data-store-handle"
            ]
        )
        store = pull_content(page_url)
        location_name = row.find(
            "button", {"class": "stores-list__store-title"}
        ).text.strip()
        raw_address = (
            row.find("div", {"class": "stores-list__store-info"})
            .get_text(strip=True, separator=",").replace(" ", "")
            .strip()
            .rstrip(",")
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        try:
            phone = store.find(
                "div", {"class": "store-detail__info-phone"}
            ).text.strip()
            hours_of_operation = (
                store.find("ul", {"class": "store-detail__info-hours"})
                .get_text(strip=True, separator=" ")
                .strip()
            )
        except:
            phone = MISSING
            hours_of_operation = MISSING
        location_type = MISSING
        country_code = "US"
        if "OPENING" in phone:
            phone = MISSING
            hours_of_operation = MISSING
            location_type = "COMING_SOON"
        if "UK" in location_name:
            country_code = "UK"
            state = MISSING
        store_number = MISSING
        latitude, longitude = latlong[num].split(",")[:2]
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
