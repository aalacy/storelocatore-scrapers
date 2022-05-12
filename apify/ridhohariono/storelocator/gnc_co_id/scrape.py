from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "gnc.co.id"
LOCATION_URL = "https://www.gnc.co.id/store-locator?page={}"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    page = 1
    while True:
        page_url = LOCATION_URL.format(page)
        soup = pull_content(page_url).find("div", {"class": "row grid-view theme1"})
        if not soup.find("div"):
            break
        contents = soup.find_all("div", {"class": "card product-card"})
        for row in contents:
            info = (
                row.find("div", {"class": "product-desc"})
                .get_text(strip=True, separator="@@")
                .replace("@@....", "")
                .split("@@")
            )
            location_name = info[0].strip()
            raw_address = ",".join(info[1:-1])
            street_address, city, state, zip_postal = getAddress(raw_address)
            addr = raw_address.split(",")
            if len(addr) > 2 and "Lt." not in addr[1] and "Guardian" not in addr[1]:
                city = addr[1]
            elif len(addr) == 2:
                city = addr[0]
                if street_address is MISSING:
                    street_address = addr[1]
            if "Medan" in street_address:
                city = "Medan"
            if "Jakarta" in street_address and city == MISSING:
                city = "Jakarta"
            if "Jakarta" in city:
                state = "D.K.I Jakarta"
            if "Guardian" or "Lt." or "Carrefour" in city:
                city = MISSING
            if zip_postal.isnumeric() is False:
                zip_postal = MISSING
            phone = info[-1] if info[-1] != "0" else MISSING
            country_code = "ID"
            store_number = MISSING
            hours_of_operation = MISSING
            latitude = MISSING
            longitude = MISSING
            location_type = MISSING
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
        page += 1


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
