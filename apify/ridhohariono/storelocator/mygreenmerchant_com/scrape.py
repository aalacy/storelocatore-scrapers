from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "mygreenmerchant.com"
BASE_URL = "https://www.mygreenmerchant.com"
DATA_URL = "https://mygreenmerchant.com/page-data/about-us/page-data.json"
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


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(DATA_URL, headers=HEADERS).json()
    for row in data["result"]["data"]["allLocations"]["edges"]:
        store = row["node"]
        page_url = BASE_URL + store["ctaUrl"]
        location_name = store["title"]
        raw_address = store["address"]
        street_address, city, _, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            addr_split = raw_address.split(",")
            if len(addr_split) > 2:
                zip_postal = raw_address.split(",")[-1].strip()
        state = MISSING
        phone = store["phoneNumber"]
        country_code = "CA"
        hours_of_operation = (
            "Mon - Fri: "
            + store["storeHrsWeekday"]
            + ", Sat - Sun: "
            + store["storeHrsWeekend"]
        ).strip()
        store_number = MISSING
        location_type = MISSING
        latitude = store["geocoordinates"]["lat"]
        longitude = store["geocoordinates"]["lat"]
        log.info("Append {} => {}, {}".format(location_name, street_address, city))
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
