from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "charleys.com"
API_URL = "https://www.charleys.com/wp-admin/admin-ajax.php"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find("div", id=re.compile(r"dine-in-\d"))
    if not hoo_content:
        hoo_content = soup.find("div", id=re.compile(r"curbside-\d"))
    hours = (
        hoo_content.find("table")
        .get_text(strip=True, separator=",")
        .replace("day,", "day: ")
    ).strip()
    return hours


def fetch_data():
    log.info("Fetching store_locator data")
    payloads = {
        "action": "get_nearby_locations",
        "lat": "34.0633443",
        "lng": "-117.6508876",
        "distance": "5000",
    }
    data = session.post(API_URL, headers=HEADERS, data=payloads).json()["data"]
    for row in data:
        page_url = row["permalink"]
        location_name = row["title"].replace("&#039;", "'")
        street_address = row["street_address"].replace(
            "(Mailing address:  Ft. Benning Exchange - Harmony Church Charley's, P.O. Box 52328, zip 31995)",
            "",
        )
        city = row["city"]
        state = row["state"]
        if state == "DC":
            state = "Washington DC"
        zip_postal = (
            MISSING if row["zip"] == "0" or len(row["zip"]) == 0 else row["zip"]
        )
        phone = row["phone"]
        country_code = "US"
        if zip_postal is not MISSING:
            if len(zip_postal.split("-")) == 1:
                if zip_postal.isnumeric() is False or state == "Ontario":
                    country_code = "CA"
                if len(zip_postal) < 5:
                    country_code = MISSING
        store_number = row["store_num"]
        hours_of_operation = get_hoo(page_url)
        latitude = row["lat"]
        longitude = "-97.2478" if row["lng"] == "-972478" else row["lng"]
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
