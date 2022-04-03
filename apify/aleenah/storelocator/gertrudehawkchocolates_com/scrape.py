from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re
import json

DOMAIN = "gertrudehawkchocolates.com"
BASE_URL = "https://gertrudehawkchocolates.com"
LOCATION_URL = "https://gertrudehawkchocolates.com/find_a_store"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    stores = soup.find_all("div", {"name": "leftLocation"})
    jso = json.loads(re.findall(r'"items":(\[[^]]+\])', str(soup))[0])
    for store in stores:
        info = (
            store.find("div", {"class": "amlocator-store-information"})
            .get_text(strip=True, separator="@@")
            .replace("@@Distance", "")
            .split("@@")
        )
        location_name = info[0].strip()
        raw_address = ", ".join(info[1:-1])
        street_address, city, state, zip_postal = getAddress(raw_address)
        if city == "Carbondale Dickson City":
            street_address = street_address + " " + city.split()[0]
            city = city.replace(city.split()[0], "")
        if len(zip_postal) < 5:
            zip_postal = "0" + zip_postal
        if "1201 Hooper" in street_address:
            address = raw_address.split(",")
            street_address = address[0]
            city = address[1]
            address = address[2].split()
            state = address[0] + " " + address[1]
            zip_postal = address[-1]
        phone = re.sub(r"Back Room.*", "", info[-1].replace(":", "")).strip()
        country_code = "US"
        store_number = store["data-amid"]
        location_type = MISSING
        try:
            hours_of_operation = (
                store.select_one(
                    "div.amlocator-schedule-container div.amlocator-week div.amlocator-schedule-table"
                )
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        latitude = jso[stores.index(store)]["lat"]
        longitude = jso[stores.index(store)]["lng"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
