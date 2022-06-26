from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "sense.org.uk"
BASE_URL = "https://www.sense.org.uk"
LOCATION_URL = "https://www.sense.org.uk/shop/charity-shops/?_paged="
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json; charset=UTF-8",
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
            if not street_address:
                street_address = raw_address.split(",")[0].strip()
            else:
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
    page = 1
    while True:
        soup = pull_content(LOCATION_URL + str(page))
        contents = soup.select("ul.list--block li")
        if not contents:
            break
        for row in contents:
            page_url = row.find("a")["href"]
            location_name = row.find("h2").text.strip()
            store = pull_content(page_url)
            info = store.find("div", {"class": "banner__content"})
            raw_address = info.find("p").get_text(strip=True, separator=",")
            street_address, city, state, zip_postal = getAddress(raw_address)
            if "SA43 1JG" in raw_address:
                zip_postal = "SA43 1JG"
            if len(street_address) < 4:
                street_address = raw_address.split(",")[0].strip()
            phone = info.find("dl").find("dd").text.strip()
            if "tba" in phone.lower() or "tbc" in phone.lower() or "email" in phone:
                phone = MISSING
            country_code = "UK"
            store_number = MISSING
            hours_of_operation = (
                store.find("h2", text="Opening hours")
                .find_next("dl")
                .get_text(strip=True, separator=" ")
            )
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
        page = page + 1


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
