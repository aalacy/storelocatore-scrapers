# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "100montaditos.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Referer": "https://spain.100montaditos.com/es/encuentranos",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://spain.100montaditos.com/assets/web/js/script.js"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        json_str = (
            stores_req.text.split("JSON.parse('")[1]
            .strip()
            .split("')}")[0]
            .strip()
            .replace('\\"', "'")
            .strip()
            .replace("\\'", "'")
            .strip()
        )

        state_json_str = (
            stores_req.text.split("JSON.parse('")[2].strip().split("')}")[0].strip()
        )
        states_json = json.loads(state_json_str)
        state_dict = {}
        for st in states_json:
            if st["post_type"] == "provincias":
                state_dict[str(st["ID"])] = st["post_title"]

        stores = json.loads(json_str)
        for store in stores:
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["ciudad"]

            raw_address = store["direccion"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            state_code = store["provincia"][0]
            state = "<MISSING>"
            if state_code in state_dict:
                state = state_dict[state_code]
            zip = store["cp"]

            city = store["ciudad"]

            country_code = "ES"
            store_number = "<MISSING>"

            phone = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude = store["latitud"]
            longitude = store["longitud"]
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
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
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
