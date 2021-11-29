from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "rustans.com"
LOCATION_URL = "https://rustans.com/pages/store-finder"
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
    contents = soup.select("div.shogun-accordion-body div[data-col-grid-mode-on]")
    for row in contents:
        info = row.find("div", {"class": "shg-rich-text shg-theme-text-content"})
        location_name = info.find("strong").text.strip()
        try:
            addr = info.find("p").get_text(strip=True, separator="@@").split("@@")
            del addr[0]
            if len(addr) > 2:
                del addr[-1]
            raw_address = ",".join(addr).strip()
        except:
            raw_address = info.select_one("div:nth-child(2)").get_text(
                strip=True, separator=","
            )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = (
            info.find("span", text=re.compile(r"\+63.*"))
            .text.split("-")[0]
            .split("and")[0]
            .split("/")[0]
            .split("Local")[0]
            .strip()
        )
        country_code = "PH"
        hoo = ""
        for val in addr:
            if "day" in val:
                hoo += val + ","
        hours_of_operation = hoo.rstrip(",")
        location_type = MISSING
        store_number = MISSING
        latlong = row.find("div", {"class": "shg-map-container"})
        latitude = latlong["data-latitude"]
        longitude = latlong["data-longitude"]
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
