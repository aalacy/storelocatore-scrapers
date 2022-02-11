from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import re


DOMAIN = "balladhealth.org"
BASE_URL = "https://www.balladhealth.org"
API_URL = "https://www.balladhealth.org/wait-times/get-locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()["data"]
    for row in data:
        info = row["attributes"]
        page_url = BASE_URL + info["path"]["alias"]
        location_name = info["title"].strip()
        if (
            not info["field_address"]["address_line2"]
            and not info["field_address"]["address_line1"]
            and not info["field_address"]["locality"]
        ):
            continue
        if not info["field_address"]["address_line2"]:
            street_address = info["field_address"]["address_line1"].strip()
        else:
            street_address = (
                info["field_address"]["address_line1"]
                + " "
                + info["field_address"]["address_line2"]
            ).strip()
        street_address = re.sub(r"\(located at .*\)", "", street_address).strip()
        city = info["field_address"]["locality"]
        state = info["field_address"]["administrative_area"]
        zip_postal = info["field_address"]["postal_code"].split("-")[0]
        if not info["field_phone"]:
            phone = MISSING
        else:
            phone = info["field_phone"].replace("\\t", "")
        country_code = info["field_address"]["country_code"]
        hours_of_operation = MISSING
        location_type = info["field_location_type"]
        store_number = info["drupal_internal__nid"]
        latitude = info["field_coordinates"]["lat"]
        longitude = info["field_coordinates"]["lon"]
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
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
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
