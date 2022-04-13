from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "untuckit.com"
BASE_URL = "https://www.untuckit.com"
LOCATION_URL = "https://www.untuckit.com/store-finder"
STORE_URL = (
    "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/5048/stores.js"
)
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


def get_hoo(url, hoo_api):
    soup = pull_content(url)
    hoo = (
        (
            re.sub(
                r"Holiday Hours.*|Black Friday.*|Easter.*|\d{2}\..*|\d{2}\/.*",
                "",
                soup.find("h2", text=re.compile(r"Hours", re.IGNORECASE))
                .find_next("p")
                .get_text(strip=True, separator=","),
                re.IGNORECASE,
            )
            .replace("|", "")
            .strip()
        )
        .rstrip(",")
        .strip()
    )
    if "day" not in hoo:
        hoo = (
            (
                bs(hoo_api, "lxml")
                .get_text(strip=True, separator="@@")
                .replace("@@See details for Holiday hours.", "")
                .split("@@")
            )[-1]
            .replace(";", ",")
            .rstrip(",")
        )
    return hoo


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(STORE_URL, headers=HEADERS).json()
    for row in data["stores"]:
        if DOMAIN in row["url"]:
            page_url = row["url"]
        else:
            page_url = BASE_URL + row["url"]
        if "news" in page_url:
            page_url = page_url.replace("news", "store-locations")
        location_name = row["name"]
        raw_address = row["address"].replace("\n", "")
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = row["phone"]
        hours_of_operation = get_hoo(page_url, row["description"]).strip()
        if "london" in raw_address.lower():
            city = "London"
            country_code = "UK"
            if "W12 7HT" in raw_address:
                zip_postal = "W12 7HT"
                street_address = re.sub(
                    r"W12 7HT", "", street_address, flags=re.IGNORECASE
                ).strip()
        elif len(zip_postal.split(" ")) > 1:
            country_code = "CA"
        else:
            country_code = "US"
        store_number = MISSING
        location_type = row["category"]
        latitude = row["latitude"]
        longitude = row["longitude"]
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
