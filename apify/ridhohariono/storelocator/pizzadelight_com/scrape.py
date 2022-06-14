import re
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "pizzadelight.com"
BASE_URL = "https://pizzadelight.com/"
LOCATION_URL = "https://www.pizzadelight.com/service/search/branch?page=all&lang=en"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return MISSING
    return field


def parse_hours(data):
    hoo = []
    for key, row in data.items():
        if not row["dining"]["range"] and not row["dining"]["range"]:
            return MISSING
        formated_hours = "{}: {} - {}".format(
            key, row["dining"]["range"][0]["from"], row["dining"]["range"][0]["to"]
        )
        hoo.append(formated_hours)
    return ", ".join(hoo)


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    for row in store_info:
        page_url = row["links"]["self"]
        location_name = handle_missing(row["title"])
        city = handle_missing(row["address"]["city"])
        street_address = handle_missing(row["address"]["address"])
        if "Marystown" not in street_address and "Cavendish" not in street_address:
            street_address = re.sub(city + ".*", "", street_address)
        street_address = re.sub(r"Hawke's Bay.*", "", street_address).strip()
        street_address = re.sub(r",$", "", street_address)
        state = handle_missing(row["address"]["province"])
        if state == "PEI":
            state = "Prince Edward Island"
        zip_postal = handle_missing(row["address"]["zip"])
        country_code = "CA"
        store_number = row["id"]
        phone = handle_missing(row["phone"])
        location_type = "OPEN"
        if row["description"]:
            if "Coming soon" in row["description"]:
                location_type = "COMING_SOON"
            elif "Closed for" in row["description"]:
                location_type = "TEMP_CLOSED"
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["lng"])
        hours_of_operation = parse_hours(row["schedule"]["week"])
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
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
