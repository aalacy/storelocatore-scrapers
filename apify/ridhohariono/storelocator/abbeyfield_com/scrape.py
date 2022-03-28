from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "abbeyfield.com"
SITE_MAP = "https://www.abbeyfield.com/sitemap"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(SITE_MAP)
    exclude_url = [
        "https://www.abbeyfield.com/dementia-friendly-care-homes/",
        "https://www.abbeyfield.com/residential-care-homes/",
        "https://www.abbeyfield.com/independent-living/",
        "https://www.abbeyfield.com/supported-housing/",
        "https://www.abbeyfield.com/nursing-homes/",
    ]
    urls = soup.find_all(
        "loc",
        text=re.compile(
            r"\/dementia-friendly-care-homes\/.*|\/residential-care-homes\/.*|\/independent-living\/.*|\/supported-housing\/.*|\/nursing-homes\/.*"
        ),
    )
    for row in urls:
        page_url = row.text.strip()
        if page_url in exclude_url:
            continue
        store = pull_content(page_url).find("section", {"class": "single-property"})
        location_name = store.find("h1", id="houseName").text.strip()
        raw_address = " ".join(store.find("p").text.replace("\n", "").strip().split())
        street_address, city, _, zip_postal = getAddress(raw_address)
        state = MISSING
        if zip_postal == MISSING:
            zip_postal = raw_address.split(",")[-1].strip()
        phone = store.find("a", {"href": re.compile("tel:.*")}).text.strip()
        country_code = "GB"
        hours_of_operation = MISSING
        store_number = MISSING
        location_type = MISSING
        latlong = (
            store.find("div", {"class": "map-container"})
            .find("a", {"class": "button secondary"})["href"]
            .split("@")[1]
            .split(",15z/")[0]
            .split(",")
        )
        latitude = latlong[0]
        longitude = latlong[1]
        log.info("Append {} => {}, {}".format(location_name, street_address, city))
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
