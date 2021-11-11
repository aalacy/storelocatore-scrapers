import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa
import json

DOMAIN = "dreamdinners.com"
BASE_URL = "https://www.dreamdinners.com/"
LOCATION_URL = "https://dreamdinners.com/main.php?page=locations"
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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = soup.find(
        "script", string=re.compile(r"var\s+simplemaps_usmap_mapdata\s+=\s+(.*);")
    )
    data = json.loads(
        re.search(r"var\s+simplemaps_usmap_mapdata\s+=\s+(.*);", data.string).group(1)
    )
    for key, val in data["locations"].items():
        page_url = BASE_URL + val["url"]
        store = pull_content(page_url).find(
            "div", {"class": "col-lg-6 text-center text-md-left"}
        )
        location_name = store.find(
            "h3", {"class": "text-uppercase font-weight-bold"}
        ).text.strip()
        raw_address = store.find("div").find("p").get_text(strip=True, separator=" ")
        street_address, city, state, zip_postal = getAddress(raw_address)
        if "339 A" in street_address:
            street_address = "339 A North El Camino Real"
            city = "Encinitas"
        city = city.replace("Sunnybrook Shopping Center", "").strip()
        phone = store.find("div").find("a").text.strip()
        country_code = "US"
        store_number = key
        location_type = MISSING
        latitude = val["lat"]
        longitude = val["lng"]
        hours_of_operation = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
