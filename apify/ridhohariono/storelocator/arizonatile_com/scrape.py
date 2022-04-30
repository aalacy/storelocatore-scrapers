from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "arizonatile.com"
BASE_URL = "https://www.arizonatile.com/"
LOCATION_URL = "https://www.arizonatile.com/api/v1/locations"
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
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    for row in store_info:
        page_url = BASE_URL + row["url"]
        location_name = row["title"].strip()
        street_address = row["streetAddress"]
        city = row["city"].replace("(DFW Airport)", "")
        state = row["state"]
        zip_postal = row["zipcode"]
        country_code = "US"
        store_number = "<MISSING>"
        phone = "503-519-8371" if len(row["primaryPhone"]) == 0 else row["primaryPhone"]
        if "COMING SOON" in location_name.upper():
            location_type = "COMING_SOON"
        else:
            location_type = "OPEN"
        latitude = row["latitude"]
        longitude = row["longitude"]
        if row["serializableShowroomHours"]:
            hoo = ""
            for key, val in row["serializableShowroomHours"].items():
                hoo += key + val.replace(".", "") + ","
            hours_of_operation = re.sub(r",$", "", hoo)
        else:
            hours_of_operation = "<MISSING>"
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
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
