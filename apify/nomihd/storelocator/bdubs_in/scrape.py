# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "buffalowildwings.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://buffalowildwings.in/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        json_str = search_res.text.split("var allLocations = ")[1].split("];")[0] + "]"

        stores = json.loads(json_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url

            location_name = store["clientName"].strip()

            location_type = "<MISSING>"

            raw_address = store["restaurantAddress"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state

            zip = formatted_addr.postcode
            if not zip:
                zip = raw_address.split(" ")[-1].strip()

            country_code = "IN"

            phone = store["clientNumber"].split(",")[0].strip()

            hour_info = store["clientSchedulingDetail"]

            hours = []
            for day in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
                start = hour_info[f"{day}RestStartTime"]
                end = hour_info[f"{day}RestEndTime"]
                hours.append(f"{day.upper()}: {start} - {end}")

            hours_of_operation = "; ".join(hours)

            store_number = store["recordId"]

            latitude, longitude = store["addressLatitude"], store["addressLongitude"]
            if latitude == longitude:
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
                raw_address=raw_address,
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
