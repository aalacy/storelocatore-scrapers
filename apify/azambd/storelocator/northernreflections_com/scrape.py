import time
import json

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog

locator_domain = "northernreflections.com"
targetRootUrl = (
    "http://cdn.storelocatorwidgets.com/json/2b102d0e60feaf5302918e33d51e67ab"
)
MISSING = "<MISSING>"
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetchStores():
    response = session.get(targetRootUrl)
    return json.loads(response.text.replace("slw(", "")[:-1])["stores"]


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores found = {len(stores)}")

    for store in stores:
        store_number = store["storeid"]
        data = store["data"]
        address = data["address"].split(", ")
        addressLen = len(address)
        page_url = MISSING
        location_name = store["name"]
        street_address = address[0]
        city = address[addressLen - 4]
        state = address[addressLen - 3]
        zip_postal = address[addressLen - 2]
        phone = data["phone"].replace("Shop By Phone: ", "")
        latitude = str(data["map_lat"])
        longitude = str(data["map_lng"])
        hours_of_operation = []

        for day in days:
            key = f"hours_{day}"
            if key in data:
                hours_of_operation.append(f"{day}: {data[key]}")
        hours_of_operation = "; ".join(hours_of_operation)
        raw_address = data["address"]

        yield SgRecord(
            locator_domain=locator_domain,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=MISSING,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="CA",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total row added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
