from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "igastoresbc.com"
LOCATION_URL = "https://www.igastoresbc.com/find-a-store/"
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
    contents = soup.find("table", {"id": "stores-data"}).find("tbody").find_all("tr")
    for row in contents:
        page_url = row.select_one("td:nth-child(3)").text.strip()
        store = (
            pull_content(page_url).find("div", {"class": "dove-gray all"}).find("table")
        )
        location_name = row.select_one("td:nth-child(2)").text.strip()
        raw_address = (
            store.find("tr")
            .find_all("td")[1]
            .get_text(strip=True, separator=",")
            .replace("Address:", "")
        ).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "CA"
        phone = re.sub(
            r"Customer Service.*",
            "",
            store.select_one("tr:nth-child(2)")
            .find_all("td")[1]
            .text.strip()
            .replace("Bakery / Deli", "")
            .replace("Phone:", ""),
        ).strip()
        store_number = MISSING
        hours_of_operation = (
            store.select_one("tr:nth-child(3)")
            .find_all("td")[1]
            .get_text(strip=True, separator=",")
            .replace("Hours:", "")
        ).strip()
        location_type = MISSING
        latitude = row.select_one("td:nth-child(7)").text.strip()
        longitude = row.select_one("td:nth-child(8)").text.strip()
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
