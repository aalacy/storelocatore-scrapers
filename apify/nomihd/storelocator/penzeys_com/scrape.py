# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "penzeys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.penzeys.com/locations/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.penzeys.com/api/GetLocations"
    stores = session.get(search_url, headers=headers).json()["Locations"]

    for store in stores:
        page_url = "https://www.penzeys.com/locations/"

        locator_domain = website
        location_name = "Penzeys"

        street_address = store["Address1"]
        if "Address2" in store:
            street_address = street_address + ", " + store["Address2"]

        street_address = (
            street_address.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "")
            .strip()
        )
        city = store["City"]
        state = store["State"]["Code"]
        zip = store["Zip"]

        country_code = "US"
        store_number = store["StoreId"]
        phone = ""
        if "Phone" in store:
            phone = (
                store["Phone"]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "")
                .strip()
            )

        location_type = "<MISSING>"
        if store["IsActive"] is False:
            location_type = "NOW CLOSED"

        hours = store.get("HoursOfOperation", [])
        hours_list = []
        for hour in hours:
            day = hour["daysOfWeek"]
            if day == "NOW OPEN":
                continue
            time = hour["timeOpen"] + " - " + hour["timeClose"]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["Lat"]
        longitude = store["Long"]
        if latitude == longitude == 0:
            latitude = longitude = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
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
