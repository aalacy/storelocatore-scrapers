import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tofs_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.tofs.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://api-cdn.storepoint.co/v1/15f4fbe5b10e3d/locations?rq"
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    loclist = loclist["results"]["locations"]
    for loc in loclist:

        location_name = loc["name"]
        log.info(location_name)
        store_number = loc["id"]
        latitude = loc["loc_lat"]
        longitude = loc["loc_long"]
        address_raw = loc["streetaddress"]
        pa = parse_address_intl(address_raw)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING

        country_code = "UK"
        location_type = loc["tags"]
        phone = loc["phone"]
        mon = loc["monday"]
        tues = loc["tuesday"]
        wed = loc["wednesday"]
        thurs = loc["thursday"]
        fri = loc["friday"]
        sat = loc["saturday"]
        sun = loc["sunday"]

        hours_of_operation = (
            "Mon: "
            + mon
            + ", Tues: "
            + tues
            + ", Wed: "
            + wed
            + ", Thurs: "
            + thurs
            + ", Fri: "
            + fri
            + ", Sat: "
            + sat
            + ", Sun: "
            + sun
        )
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url="https://www.tofs.com/pages/store-finder",
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
            raw_address=address_raw,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
