from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "theuniformoutlet.com"
BASE_URL = "https://www.theuniformoutlet.com"
LOCATION_URL = "https://theuniformoutlet.com/find-a-store/"
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


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find("div", {"class": "content-left"})
    try:
        hoo_content.find("div", {"class": "post-thumb"}).decompose()
        hoo_content.find("p", {"style": "text-align: center;"}).decompose()
        hoo_content.find("h3").decompose()
    except:
        pass
    for content in hoo_content.find_all("p"):
        if re.match(r"Store Hours", content.text.strip(), re.IGNORECASE):
            content.decompose()
            break
        content.decompose()
    hours_of_operation = (
        re.sub(
            r",Holiday Hours.*",
            "",
            ",".join([hoo.text.strip() for hoo in hoo_content.find_all("p")]).strip(),
            re.IGNORECASE,
        )
        .strip()
        .rstrip(",")
    )
    return hours_of_operation


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.page-content.page-content--centered a")
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url)
        info = store.find("div", {"class": "page-content page-content--centered"})
        location_name = store.find("h1", {"class": "page-heading"}).text.strip()
        raw_address = (
            info.find("strong", text="Address:")
            .parent.text.replace("Address:", "")
            .replace(" ", "")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = info.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
        country_code = "US"
        hours_of_operation = (
            info.find("table")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace(",to,", " - ")
            .strip()
        )
        country_code = "US"
        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
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
