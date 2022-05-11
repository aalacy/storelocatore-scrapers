from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "zupans.com"
BASE_URL = "https://www.zupans.com"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    contents = soup.find(
        "div", {"class": "max-w-container-xl w-full mx-auto p-6"}
    ).find_all("a", {"class": "link mb-6 mr-6"})
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url)
        location_name = store.find("h1", {"itemprop": "name"}).text.strip()
        raw_address = store.find("address").get_text(strip=True, separator=" ")
        street_address = store.find("div", {"itemprop": "streetAddress"}).text.strip()
        city = store.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = store.find("span", {"itemprop": "addressRegion"}).text.strip()
        zip_postal = store.find("span", {"itemprop": "postalCode"}).text.strip()
        phone = store.find("a", {"itemprop": "telephone"}).text.strip()
        country_code = "US"
        store_number = MISSING
        hours_of_operation = (
            store.find("div", {"class": "w-full max-w-xs"})
            .find("div", {"class": "mb-6"})
            .find("p")
            .text.strip()
        )
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


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
