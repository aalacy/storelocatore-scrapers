from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "jonsmithsubs.com"
BASE_URL = "https://www.jonsmithsubs.com"
LOCATION_URL = "https://www.jonsmithsubs.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


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
    content = (
        soup.find("div", {"id": "locations"})
        .find("div", {"class": "pm-location-search-list"})
        .find_all("div", {"class": "col-md-4 col-xs-12 pm-location"})
    )
    more_locs = soup.find("section", {"id": "more-locs"}).find_all("section")
    for row in content:
        if "Coming Soon!" in row.text.strip():
            continue
        location_name = row.find("h4").text.strip()
        url_content = row.find("a", text="View Menu & Details")
        if not url_content:
            page_url = LOCATION_URL
        else:
            page_url = BASE_URL + row.find("a", text="View Menu & Details")["href"]
        raw_address = row.find("a", {"class": "address-link"}).get_text(
            strip=True, separator=" "
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = MISSING
        phone = row.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
        if "Temporarily Closed" in row.text.strip():
            location_type = "TEMPORARILY CLOSED"
        else:
            location_type = "PRIMARY LOCATION"
        latitude = MISSING
        longitude = MISSING
        hours_of_operation = (
            row.find("div", {"class": "hours"})
            .get_text(strip=True, separator=",")
            .replace(",:,", ": ")
            .replace("-,", "- ")
            .replace("00,", "00 ")
        )
        if "Temporarily Closed" in hours_of_operation:
            hours_of_operation = MISSING
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

    for row in more_locs:
        info = row.get_text(strip=True, separator="@").split("@")
        location_name = info[0]
        raw_address = " ".join(info[1:-1])
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = MISSING
        phone = info[-1]
        location_type = "LOCATIONS IN SOUTH FLORIDA"
        latitude = MISSING
        longitude = MISSING
        hours_of_operation = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
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
