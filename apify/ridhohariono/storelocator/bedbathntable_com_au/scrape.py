from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl


DOMAIN = "bedbathntable.com.au"
LOCATION_URL = "https://www.bedbathntable.com.au/locator"
API_URL = "https://www.bedbathntable.com.au/amlocator/index/ajax/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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
    payload = {
        "lat": "0",
        "lng": "0",
        "radius": "0",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
        "regionId": "0",
    }
    data = session.post(API_URL, headers=HEADERS, data=payload).json()
    stores = pull_content(LOCATION_URL).select("div.amlocator-store-desc")
    num = 0
    for row in data["items"]:
        info = bs(row["popup_html"], "lxml")
        page_url = info.find("a", {"class": "amlocator-link"})["href"]
        location_name = info.find("a", {"class": "amlocator-link"}).text.strip()
        raw_address = info.find("div", {"class": "amlocator-address"}).get_text(
            strip=True, separator=","
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            zip_postal = info.find("div", {"class": "amlocator-zip"}).text.strip()
        country_code = "AU"
        phone = stores[num].find("div", {"class": "phone"}).text.strip()
        try:
            hours_of_operation = (
                stores[num]
                .find("div", {"class": "amlocator-schedule-table"})
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        location_type = MISSING
        store_number = row["id"]
        latitude = row["lat"]
        longitude = row["lng"]
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
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
