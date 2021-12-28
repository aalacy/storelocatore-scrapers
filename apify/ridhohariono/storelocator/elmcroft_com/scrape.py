from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "elmcroft.com"
BASE_URL = "https://www.elmcroft.com"
LOCATION_URL = "https://www.elmcroft.com/community-results/?cq=90001&lo=&am=&dist=8016096916B94309A828CDF99707584D&pgc={}"
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


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    page = 0
    while True:
        results = (
            pull_content(LOCATION_URL.format(page))
            .find("div", {"class": "location-results"})
            .find_all("div", {"class": "col-md-12 results"})
        )
        if not results:
            break
        for row in results:
            page_url = BASE_URL + row.find("a")["href"]
            location_name = row.find("h4", {"class": "fn blue"}).text.strip()
            map_link = row.find("a", {"aria-label": "Get Directions"})["href"]
            for el in row.find("address").find_all("a"):
                el.decompose()
            info = (
                row.find("address")
                .get_text(strip=True, separator="@")
                .strip()
                .split("@")
            )
            raw_address = " ".join(" ".join(info[:-1]).split())
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = info[-1]
            location_type = row.find("div", {"class": "living-options-list"}).get_text(
                strip=True, separator=","
            )
            store_number = MISSING
            country_code = "US"
            latitude, longitude = get_latlong(map_link)
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
        page += 1


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
