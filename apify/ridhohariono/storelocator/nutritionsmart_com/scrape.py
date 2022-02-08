from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "nutritionsmart.com"
BASE_URL = "https://www.nutritionsmart.com"
LOCATION_URL = "https://www.nutritionsmart.com/store-locations/"
HEADERS = {
    "Accept": "application/json",
    "Content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
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
    contents = soup.select(
        "div.elementor-element.elementor-align-center.elementor-widget.elementor-widget-button a.elementor-button-link.elementor-button.elementor-size-sm.elementor-animation-grow"
    )
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url)
        location_name = store.find(
            "h3", {"class": "elementor-heading-title elementor-size-default"}
        ).text.strip()
        info = store.select(
            "div.elementor-element.elementor-position-left.elementor-view-default.elementor-vertical-align-top.elementor-widget.elementor-widget-icon-box"
        )
        raw_address = " ".join(
            info[2].get_text(strip=True, separator=",").replace("Address,", "").split()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        if "464 Sw Port" in street_address:
            street_address = "464 Sw Port St. Lucie Blvd"
            city = "Port St. Lucie"
        country_code = "US"
        phone = store.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
        hours_of_operation = (
            " ".join(info[3].get_text(strip=True, separator=",").split())
            .replace("Store Hours,", "")
            .strip()
        )
        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
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


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
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
