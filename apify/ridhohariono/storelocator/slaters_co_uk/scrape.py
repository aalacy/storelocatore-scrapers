import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "slaters.co.uk"
BASE_URL = "https://slaters.co.uk"
LOCATION_URL = "https://slaters.co.uk/store-locator"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
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
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_latlong(soup):
    content = soup.find(
        "script",
        type="text/x-magento-init",
        string=re.compile("Slaters_StoreLocator/js/store-locator-detail.*"),
    )
    latitude = re.search(
        r'"lat":\s+(-?[\d]*\.[\d]*),$', content.string, re.MULTILINE
    ).group(1)
    longitude = re.search(
        r'"lng":\s+(-?[\d]*\.[\d]*),$', content.string, re.MULTILINE
    ).group(1)
    return latitude, longitude


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    links = soup.find_all("a", {"class": "store-item"})
    for link in links:
        page_url = link["href"]
        content = pull_content(page_url)
        info = content.find("div", {"class": "stores-wrapper j-stores-wrapper"})
        location_name = info.find("h1", {"class": "store-name"}).text
        raw_address = info.find("p", {"class": "address"}).text.strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING and len(raw_address.split(",")) == 3:
            zip_postal = raw_address.split(",")[-1]
        store_number = MISSING
        phone = info.find("a", {"class": "phone"}).text.strip()
        country_code = "UK"
        location_type = "slaters"
        latitude, longitude = get_latlong(content)
        hours_of_operation = (
            info.find("ul", {"class": "store-info j-store-info"})
            .find("li")
            .get_text(strip=True, separator=",")
            .replace("Opening Hours,", "")
            .replace("day,", "day: ")
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
