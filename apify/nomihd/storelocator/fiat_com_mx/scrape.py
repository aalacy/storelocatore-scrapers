# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fiat.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.fiat.com.mx/hostb/fiat_mx/JSONConversion/fiat/fiat-distribuidor.json"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)

        stores = json_res["sales"]

        for store in stores:

            locator_domain = website

            page_url = store["website"]
            if not page_url:
                page_url = "https://www.fiat.com.mx/distribuidores.html"

            location_name = store["dealerName"].strip()

            location_type = "<MISSING>"

            street_address = store["dealerAddress1"]

            city = store["dealerCity"]

            state = store["dealerState"]

            zip = store["dealerZipCode"]

            country_code = "MX"

            phone = store["phoneNumber"]
            if phone:
                phone = phone.lower().split("y")[0].strip().split("/")[0].strip()

            hours_of_operation = store["openingDaysHours"]["Open"]

            store_number = store["dealerCode"]

            latitude, longitude = (
                store["dealerShowroomLatitude"],
                store["dealerShowroomLongitude"],
            )
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
