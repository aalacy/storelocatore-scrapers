import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re


DOMAIN = "mandsopticians.com"
BASE_URL = "https://mandsopticians.com"
LOCATION_URL = "https://mandsopticians.com/stores"
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
    contents = soup.select("div.amlocator-store-desc")
    script_content = soup.find(
        "script", string=re.compile(r'\{"items":.*')
    ).string.strip()
    json_info = json.loads(re.search(r'\{"items":(\[.*\])', script_content).group(1))
    num = 0
    for row in contents:
        page_url = (
            BASE_URL
            + row.find("div", {"class": "store-link"}).find(
                "a", {"class": "store-info"}
            )["href"]
        )
        location_name = row.find("div", {"class": "amlocator-title"}).text.strip()
        raw_address = (
            row.find("div", {"class": "address"}).text.replace("\n", "").strip()
        )
        street_address, city, state, _ = getAddress(raw_address)
        zip_postal = json_info[num]["zip"]
        if "Da9 9Sd" in street_address:
            city = "Greenhithe"
            zip_postal = "DA9 9SD"
            street_address = (
                street_address.replace("Da9 9Sd", "").replace(city, "").strip()
            )
        if "Hedge End" in city:
            city = city.replace("Southampton", "").strip()
        city = city.replace("St Albans", "")
        phone = row.find("div", {"class": "telephone"}).text.strip()
        country_code = "UK"
        hours_of_operation = (
            row.find("div", {"class": "amlocator-week"})
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .strip()
        )
        location_type = "EYE_TEST"
        store_number = json_info[num]["id"]
        latitude = json_info[num]["lat"]
        longitude = json_info[num]["lng"]
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
        num += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    results = fetch_data()
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
