from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "balduccis.com"
BASE_URL = "https://balduccis.com"
LOCATION_URL = "https://local.balduccis.com/"
SITE_MAP = "https://local.balduccis.com/sitemap.xml"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
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
    soup = pull_content(SITE_MAP)
    for row in soup.find_all("url"):
        page_url = row.find("loc").text
        check = page_url.replace(LOCATION_URL, "").split("/")
        if len(check) < 3:
            continue
        soup = pull_content(page_url)
        content = soup.find("div", {"class": "Core-container"})
        location_name = (
            soup.find("h1", {"class": "ContentBanner-h1"})
            .text.replace("\n", " ")
            .strip()
        )
        raw_address = re.sub(
            r"(,){2,}",
            ",",
            content.find("address", {"id": "address"}).get_text(
                strip=True, separator=","
            ),
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = content.find("div", {"id": "phone-main"}).text.strip()
        hours_of_operation = (
            content.find("table", {"class": "c-hours-details"})
            .find("tbody")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace(",-,", " - ")
        )
        store_number = MISSING
        country_code = content.find("address", {"id": "address"})["data-country"]
        location_type = "balduccis"
        latitude = content.find("meta", {"itemprop": "latitude"})["content"]
        longitude = content.find("meta", {"itemprop": "longitude"})["content"]
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
