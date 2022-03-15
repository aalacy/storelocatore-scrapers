import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rossy_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.rossy.ca/en/store-finder/",
}

DOMAIN = "https://rossy.ca"
MISSING = SgRecord.MISSING


def fetch_data():
    payload = (
        "/ajax/ajaxcall.php?langID=1&do=getLocations&q=E1c5a3&distance=10000&units=km"
    )
    location_url = "https://www.rossy.ca/ajax/store-finder.php?langID=1&"
    r = session.post(location_url, data=payload, headers=headers)
    r.encoding = "utf-8-sig"
    json_data = json.loads(r.json()["stores"])
    for value in json_data:
        location_name = value["city"] + "(" + value["store"] + ")"
        log.info(location_name)
        try:
            street_address = value["address"] + " " + value["address2"]
        except:
            street_address = value["address"]
        city = value["city"]
        state = value["province"]
        zip_postal = value["postalCode"]
        country_code = value["country"]
        store_number = value["store"]
        phone = value["telephone"]
        location_type = MISSING
        latitude = value["latitude"]
        longitude = value["longitude"]
        try:
            mo = "Monday: " + value["mondayHours"]
            tu = ",Tuesday: " + value["tuesdayHours"]
            we = ",Wednesday: " + value["wednesdayHours"]
            th = ",Thursday: " + value["thursdayHours"]
            fr = ",Friday: " + value["fridayHours"]
            sa = ",Saturday: " + value["saturdayHours"]
            su = ",Sunday: " + value["sundayHours"]
            hours_of_operation = mo + tu + we + th + fr + sa + su
        except:
            hours_of_operation = MISSING
        if "Monday: ,Tuesday: ,Wednesday" in hours_of_operation:
            hours_of_operation = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url="https://www.rossy.ca/en/store-finder/",
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
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
