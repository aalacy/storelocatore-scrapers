import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa

DOMAIN = "lowes.com"
SITE_MAP = "https://www.lowes.com/content/lowes/desktop/en_us/stores.xml"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


MISSING = "<MISSING>"


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
    HEADERS["Referer"] = url
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except:
        log.info("[RETRY] Pull content => " + url)
        pull_content(url)
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = pull_content(SITE_MAP).find_all("loc")
    for row in page_urls:
        page_url = row.text.strip()
        store = pull_content(page_url)
        info = json.loads(
            re.search(
                r"window\['__PRELOADED_STATE__'\]\s+=\s+(.*)",
                store.find(
                    "script", string=re.compile(r"window\['__PRELOADED_STATE__'\].*")
                ).string,
            ).group(1)
        )["storeDetails"]
        location_name = store.find("h1", id="storeHeader").text.strip()
        raw_address = store.find("div", {"class": "location"}).get_text(
            strip=True, separator=","
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = store.find("span", {"data-id": "sc-main-phone"}).text.strip()
        country_code = info["country"]
        store_number = page_url.split("/")[-1]
        hours_of_operation = (
            store.find("div", id="hours-content")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace(",-,", " - ")
            .strip()
        )
        latitude = info["lat"]
        longitude = info["long"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
