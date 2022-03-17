from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "nenechicken.com.au"
LOCATION_URL = "http://www.nenechicken.com.au/pages/locations.php"
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


def get_addr_info(raw_address):
    try:
        return re.match(
            r",?.*,?.*,(?P<city>\D+),?\s+?(?P<state>\D+)(?P<zip_postal>\s+\d{3,4})$",
            raw_address,
        ).groupdict()
    except:
        pass
    try:
        return re.match(
            r",?.*,?.*,?\s+?(?P<city>\D+),?\s+?(?P<state>\D+)(?P<zip_postal>\s+\d{3,4})$",
            raw_address,
        ).groupdict()
    except:
        pass
    try:
        return re.match(
            r",?.*,?.*,(?P<zip_postal>\s+\d{3,4})(?P<city>\D+),\s+?(?P<state>\D+)$",
            raw_address,
        ).groupdict()
    except:
        return False


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.modal.fade")
    for row in contents:
        info = row.find("div", {"class": "modal-body"})
        location_type = MISSING
        country_code = "AU"
        store_number = MISSING
        latitude = MISSING
        longitude = MISSING
        if info.find("div", {"class": "expand"}):
            parent = info.find_all("div", {"class": "xx"})
            for store in parent:
                location_name = (
                    store.find("h3", {"class": "title text-large"}).text.strip().title()
                )
                if "Coming Soon" in location_name:
                    continue
                info = store.find_next("div", {"class": "expand"})
                raw_address = (
                    info.find_next("p")
                    .get_text(strip=True, separator=",")
                    .replace("Shop address:,", "")
                    .strip()
                )
                addr_optional = get_addr_info(raw_address)
                if not raw_address:
                    raw_address = (
                        location_name.replace("(", "").replace(")", "").strip()
                    )
                    street_address = MISSING
                    city = MISSING
                    state = MISSING
                    zip_postal = MISSING
                else:
                    street_address, city, state, zip_postal = getAddress(raw_address)
                    if street_address == MISSING:
                        street_address = " ".join(raw_address.split(",")[:-1])
                    if city == MISSING and addr_optional:
                        if "Victoria" in raw_address:
                            city = "Victoria"
                        else:
                            city = addr_optional["city"].replace(",", " ").strip()
                    if state == MISSING and addr_optional:
                        state = addr_optional["state"].strip()
                    if zip_postal == MISSING and addr_optional:
                        zip_postal = addr_optional["zip_postal"].upper().strip()
                phone = re.sub(
                    r"Store number:|\(Pickup Only\)",
                    "",
                    info.find_next("p").find_next("p").text.replace("\n", " ").strip(),
                    flags=re.IGNORECASE,
                ).strip()
                hours_of_operation = (
                    info.find_next("p")
                    .find_next("p")
                    .find_next("p")
                    .get_text(strip=True, separator=",")
                    .replace("Trading hours:,", "")
                    .strip()
                )
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
        else:
            title = info.find_all("h3", {"class": "title text-large"})
            for store in title:
                location_name = store.text.strip().title()
                raw_address = store.find_next("p").get_text(strip=True, separator=",")
                addr_optional = get_addr_info(raw_address)
                if not raw_address:
                    continue
                phone = (
                    store.find_next("p")
                    .find_next("p")
                    .text.replace("\n", " ")
                    .replace("Phone :", "")
                    .strip()
                )
                hours_of_operation = (
                    store.find_next("p")
                    .find_next("p")
                    .find_next("p")
                    .get_text(strip=True, separator=",")
                    .replace("Trading hours:,", "")
                    .strip()
                )
                street_address, city, state, zip_postal = getAddress(raw_address)
                if street_address == MISSING:
                    street_address = " ".join(raw_address.split(",")[:-1])
                if city == MISSING and addr_optional:
                    if "Victoria" in raw_address:
                        city = "Victoria"
                    else:
                        city = addr_optional["city"].replace(",", " ").strip()
                if state == MISSING and addr_optional:
                    state = addr_optional["state"].strip()
                if zip_postal == MISSING and addr_optional:
                    zip_postal = addr_optional["zip_postal"].upper().strip()
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
                    SgRecord.Headers.LOCATION_NAME,
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
