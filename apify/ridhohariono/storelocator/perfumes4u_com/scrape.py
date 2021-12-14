import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "perfumes4u.com"
BASE_URL = "https://perfumes4u.com"
LOCATION_URL = "https://perfumes4u.com/contact-us/locations/"
API_URL = "https://www.perfumes4u.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=f6de3f7e82&load_all=1&layout=1"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

CANADIAN = [
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
]

PUERTO = ["PR"]


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


def parse_hoo(hoo):
    hoo = json.loads(hoo)
    hours_of_operation = ""
    for key in hoo.keys():
        hours = "CLOSED" if hoo[key][0] == "0" else hoo[key][0]
        hours_of_operation += key + ": " + hours + ","
    return hours_of_operation


def fetch_data():
    log.info("Fetching store_locator data")
    stores = session.get(API_URL, headers=HEADERS).json()
    for row in stores:
        page_url = LOCATION_URL
        location_name = row["title"].strip()
        street_address = row["street"]
        state = row["state"]
        city = row["city"]
        zip_postal = row["postal_code"]
        phone = row["phone"]
        hours_of_operation = parse_hoo(row["open_hours"])
        store_number = row["id"]
        if state in CANADIAN:
            country_code = "CA"
        elif state in PUERTO:
            country_code = "PR"
        else:
            country_code = "US"
        location_type = "perfumes4u"
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
            raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
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
