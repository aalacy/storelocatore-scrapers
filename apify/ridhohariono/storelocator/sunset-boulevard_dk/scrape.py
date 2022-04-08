import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "sunset-boulevard.dk"
BASE_URL = "https://sunset-boulevard.dk"
LOCATION_URL = "https://sunset-boulevard.dk/restauranter/"
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
    contents = soup.select("div.map-container div.marker.custom-marker")
    for row in contents:
        page_url = row.find("a", {"class": "show-restaurant"})["href"]
        store = pull_content(page_url)
        info = (
            store.select(
                "div.elementor-widget.elementor-widget-theme-post-title.elementor-page-title.elementor-widget-heading"
            )[-1]
            .parent.get_text(strip=True, separator="@@")
            .split("@@")
        )
        location_name = info[0].strip()
        raw_address = ", ".join(info[1:-1]).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            zip_postal = re.search(r"\d{4,5}", raw_address).group()
            street_address = street_address.replace(zip_postal, "").strip()
        country_code = "DK"
        try:
            phone = store.find("span", {"itemprop": "telephone"}).text.strip()
        except:
            phone = MISSING
        try:
            hours_of_operation = (
                store.find("div", {"class": "rel-open"})
                .get_text(strip=True, separator=" ")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        store_number = MISSING
        location_type = MISSING
        latitude = row["data-lat"]
        longitude = row["data-lng"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
