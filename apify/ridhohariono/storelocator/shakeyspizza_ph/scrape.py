from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "shakeyspizza.ph"
LOCATION_URL = "https://www.shakeyspizza.ph/store-locator?view=all&page={page}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


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
    i = 0
    while True:
        store_url = LOCATION_URL.format(page=i)
        soup = pull_content(store_url)
        store_numbers = soup.find_all(
            "input",
            {"class": "edit-storeinformation button js-form-submit form-submit"},
        )
        if not store_numbers:
            break
        for number in store_numbers:
            store_number = number["name"].replace("store_", "")
            page_url = f"https://www.shakeyspizza.ph/store-locator?view=details&store={store_number}&destination=/store-locator%3Fview%3Dall%26page%3D0"
            store = pull_content(page_url)
            location_name = store.find("div", id="edit-name").text.strip()
            raw_address = store.find("textarea", id="edit-address").text.strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = store.find("a", {"class": "store-finder-tel"}).text.strip()
            country_code = "PH"
            location_type = MISSING
            hours_24 = store.find(
                "div",
                {"class": "store-details-twentyfourhours js-form-wrapper form-wrapper"},
            )
            if not hours_24:
                hours_of_operation = (
                    store.find("div", id="weekdays-container")
                    .get_text(strip=True, separator=",")
                    .replace("day,", "day: ")
                    .strip()
                )
            else:
                hours_of_operation = hours_24.text.strip()
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
        i += 1


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
