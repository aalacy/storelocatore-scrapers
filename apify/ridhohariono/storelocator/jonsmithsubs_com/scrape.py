from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import json
import re

DOMAIN = "jonsmithsubs.com"
BASE_URL = "https://www.jonsmithsubs.com/"
LOCATION_URL = "https://www.jonsmithsubs.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)

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
    soup = pull_content(LOCATION_URL)
    data = json.loads(
        soup.find("script", id="popmenu-apollo-state")
        .string.replace("window.POPMENU_APOLLO_STATE = ", "")
        .replace("};", "}")
        .replace('" + "', "")
        .strip()
    )
    for key, value in data.items():
        if key.startswith("RestaurantLocation:"):
            if "Coming Soon!" in value["customLocationContent"]:
                continue
            if "Acworth" in value["name"]:
                page_url = BASE_URL + value["slug"]
            else:
                page_url = BASE_URL + value["slug"] + "-" + value["state"].lower()
            location_name = value["name"]
            raw_address = value["fullAddress"].replace("\n", ", ")
            city = value["city"]
            state = value["state"]
            zip_postal = value["postalCode"]
            street_address = re.sub(
                r",?\s?" + city + r"|" + r",?\s?" + state + r"|" + zip_postal,
                "",
                value["streetAddress"]
                .replace("\n", ", ")
                .replace("Inside Galleria", "")
                .replace(", Clinton Twp", ""),
            )
            country_code = value["country"]
            phone = value["displayPhone"]
            location_type = MISSING
            store_number = MISSING
            latitude = value["lat"]
            longitude = value["lng"]
            try:
                hours_of_operation = ", ".join(value["schemaHours"])
            except:
                MISSING
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

    for key, value in data.items():
        if key.startswith("CustomPageSectionColumn:"):
            location_name = value["columnHeading"]
            info = (
                value["columnContent"].replace("\n", "@").strip().rstrip("@").split("@")
            )
            raw_address = " ".join(info[:-1])
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = "US"
            store_number = MISSING
            phone = info[-1]
            location_type = "LOCATIONS IN SOUTH FLORIDA"
            latitude = MISSING
            longitude = MISSING
            hours_of_operation = MISSING
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
