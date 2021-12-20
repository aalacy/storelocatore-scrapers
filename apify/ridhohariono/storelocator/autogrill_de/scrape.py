from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "autogrill.de"
LOCATION_URL = "https://autogrill.de/en/content/contacts"
API_URL = "https://autogrill.de/vyaggio/branches/4"
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
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
            country = data.country
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country is None or len(country) == 0:
                country = MISSING
            return street_address, city, state, zip_postal, country
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fix_coord(coord):
    result = str(coord).split(".")
    return result[0] + "." + result[1]


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        location_name = row["title"]
        raw_address = (
            bs(row["html"], "lxml")
            .get_text(strip=True, separator=",")
            .replace("Autogrill", "")
            .strip()
        ).replace("\n", " ")
        phone = re.search(r"Tel:(.*)", raw_address, re.IGNORECASE)
        if not phone:
            phone = MISSING
        else:
            phone = phone.group(1).replace("Tel: ", "").strip()
        raw_address = (
            re.sub(r"Tel.*", "", raw_address)
            .rstrip(",")
            .replace("+", "-")
            .replace("Limmtquai", "Limmatquai")
            .strip()
        )
        street_address, city, state, zip_postal, country_code = getAddress(raw_address)
        street_address = street_address.replace(state, "")
        if (
            street_address.replace(" ", "").strip().isnumeric()
            or len(street_address) == 0
            or len(street_address) < 5
        ):
            if zip_postal is not MISSING:
                street_address = " ".join(
                    raw_address.split(zip_postal)[0].split(",")[1:]
                )
            elif street_address:
                street_address = " ".join(
                    raw_address.split(street_address)[0].split(",")[1:]
                )
        store_number = row["id"]
        location_type = MISSING
        latitude = fix_coord(row["lat"])
        longitude = fix_coord(row["lon"])
        hours_of_operation = MISSING
        if "Zürich-Flughafen" in country_code:
            country_code = "DE"
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
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.RAW_ADDRESS,
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
