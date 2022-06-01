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


DOMAIN = "idealmarket.us"
BASE_URL = "https://idealmarket.com"
LOCATION_URL = "http://idealmarket.us/store-locator/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = SgRecord.MISSING


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


def parse_json(link_url, js_variable):
    soup = pull_content(link_url)
    pattern = re.compile(r"var\s+" + js_variable + r"\s+=\s+", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    if not script:
        return False
    parse = re.search(r'(?s)\(\{"map_options":\{.*\}\)', script.string)
    place = re.search(r'(?s)"places":(\[\{.*?\}\]),"map_tabs"', parse.group())
    data = json.loads(place.group(1))
    return data


def fetch_data():
    store_info = parse_json(LOCATION_URL, "map1")
    for row in store_info:
        location = row["location"]
        location_name = row["title"]
        raw_address = row["address"]
        street_address, _, _, _ = getAddress(raw_address)
        city = location["city"]
        state = location["state"]
        zip_postal = location["postal_code"]
        country_code = "US"
        store_number = row["id"]
        phone = location["extra_fields"]["phone"]
        if location["extra_fields"]["subway"]:
            location_type = "Subway"
        else:
            location_type = row["categories"][0]["name"]
        latitude = location["lat"]
        longitude = location["lng"]
        hours_of_operation = MISSING
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
