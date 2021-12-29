# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "dodgecaribbean.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.dodgecaribbean.com/content/dam/cross-regional/latam/jeep/en_cr/js/gaq-caribbean_latest.js"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)
        stores = json_res["dealers"]

        for key, stores in json_res["dealers"].items():

            for store in stores:
                locator_domain = website

                location_name = store["d_name"]
                page_url = "https://www.dodgecaribbean.com/"

                location_type = "<MISSING>"

                raw_address = store["d_address"] + ", " + store["d_city"]
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = key

                phone = store["d_phone"]

                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

                latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
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


if __name__ == "__main__":
    scrape()
