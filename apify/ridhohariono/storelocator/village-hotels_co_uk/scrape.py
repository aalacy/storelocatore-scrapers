from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "village-hotels.co.uk"
BASE_URL = "https://www.village-hotels.co.uk"
LOCATION_URL = "https://www.village-hotels.co.uk/hotels/"
HEADERS = {
    "Accept": "*/*",
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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("a.list-item--panel__trigger")
    for row in contents:
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url)
        location_name = row.find("div", {"itemprop": "name"}).text.strip()
        raw_address = re.sub(
            r"(\(.*\))", "", store.find("address", {"itemprop": "address"}).text.strip()
        )
        if "CH5 3YB" in raw_address or "WD6 3SB" in raw_address:
            zip_postal = raw_address.split(",")[-1].strip()
            raw_address = raw_address.replace(zip_postal, "").rstrip(",")
            street_address, city, state, _ = getAddress(raw_address)
        else:
            street_address, city, state, zip_postal = getAddress(raw_address)
        phone = MISSING
        country_code = "UK"
        hours_of_operation = store.find(
            "time", {"itemprop": "openingHours"}
        ).text.strip()
        location_type = MISSING
        store_number = MISSING
        latitude = store.find("meta", {"property": "place:location:latitude"})[
            "content"
        ]
        longitude = store.find("meta", {"property": "place:location:longitude"})[
            "content"
        ]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
