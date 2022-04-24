from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "churchs.com.mx"
BASE_URL = "https://www.churchs.com.mx/restaurant/detail"
API_URL = "https://churchs.com.mx/app/feed/getListAll"
STORE_INFO_API = "https://churchs.com.mx/app/feed/getLightStoreInfo&restaurant_id="
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
    data = session.get(API_URL, headers=HEADERS).json()
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for row in data["restaurants"]:
        page_url = BASE_URL + "?id=" + row["restaurant_id"]
        info = session.get(
            STORE_INFO_API + row["restaurant_id"], headers=HEADERS
        ).json()["restaurant"]
        location_name = row["name"]
        raw_address = (
            " ".join(row["name_arabic"].split()).replace(", México", "").strip()
        )
        addr_split = raw_address.split(",")
        street_address = addr_split[0].strip()
        city = re.sub(r"\d+", "", addr_split[-2]).strip()
        state = addr_split[-1].replace(".", "").strip()
        zip_postal = re.sub(r"\D+", "", addr_split[-2]).strip()
        phone = info["telephone"]
        country_code = "MX"
        location_type = "Restaurant"
        store_number = row["restaurant_id"]
        hoo = ""
        hoo_content = info["working_hours"]
        for day in days:
            try:
                if hoo_content[day]["working"] == "open":
                    hours = (
                        hoo_content[day]["start_time"]
                        + " - "
                        + hoo_content[day]["end_time"]
                    )
                else:
                    hours = "Closed"
                hoo += day.title() + ": " + hours + ", "
            except:
                hoo += day.title() + ": Closed, "
        hours_of_operation = hoo.strip().rstrip(",")
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
