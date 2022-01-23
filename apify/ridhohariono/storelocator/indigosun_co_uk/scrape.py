from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import re

DOMAIN = "indigosun.co.uk"
LOCATION_URL = "https://www.indigosun.co.uk/locations"
HEADERS = {
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
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=100,
        max_search_results=1,
    )
    for zipcode in search:
        log.info("Get store info for zip_code => " + zipcode)
        try:
            store = bs(
                session.post(LOCATION_URL, {"postcode": zipcode}).content, "lxml"
            ).find("div", {"class": "shop clearfix"})
        except:
            continue
        info = store.find("div", {"class": "opening"})
        location_name = info.find("h3").text.strip()
        addr = info.find("p").get_text(strip=True, separator=",").split("Tel:")
        raw_address = addr[0].rstrip(",")
        street_address, city, state, zip_postal = getAddress(raw_address)
        if zip_postal == MISSING:
            zip_postal = raw_address.split(",")[-1]
        if city == MISSING:
            city = raw_address.split(",")[-2]
        country_code = "GB"
        phone = addr[1].strip()
        hoo = re.sub(
            r"Opening.*|Subject to change.*|Last.*",
            "",
            info.get_text(strip=True, separator=" ")
            .replace("Opening times", "Opening Hours")
            .split("Opening Hours")[1],
        )
        hours_of_operation = " ".join(hoo.split()).strip()
        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
