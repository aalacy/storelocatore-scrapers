# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.cocobubbletea.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.cocobubbletea.com/locations"
    api_url = "https://api.storepoint.co/v1/15ef25fe59881c/locations?lat=40.7500&long=-73.1800&radius=1000"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)

        stores = json_res["results"]["locations"]

        for _, store in enumerate(stores, 1):

            page_url = search_url

            locator_domain = website
            if store["description"] == "Coming Soon!":
                continue

            location_name = store["name"].strip()

            raw_address = store["streetaddress"]

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = store["id"]

            phone = store["phone"]
            location_type = "<MISSING>"
            hour_list = []

            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]:
                time = store[day] if store[day] else "Closed"
                hour_list.append(f"{day}: {time}")

            hours_of_operation = "; ".join(hour_list)

            latitude, longitude = (
                store["loc_lat"],
                store["loc_long"],
            )

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
