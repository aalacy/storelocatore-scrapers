# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "fridaysperu.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "vh80n2gxi9.execute-api.us-east-1.amazonaws.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "accept": "application/json, text/plain, */*",
    "x-api-key": "7DFh3J4w1l7yN1qHwe33N5mQn9g9FUeD8XyBzoBn",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://fridaysperu.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://fridaysperu.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

data = '{"language":"es"}'


def fetch_data():
    # Your scraper here
    search_url = "https://fridaysperu.com/locales"
    with SgRequests() as session:
        csrf_token = (
            session.get(search_url)
            .text.split('csrfToken:"')[1]
            .strip()
            .split('",')[0]
            .strip()
        )
        headers["x-csrf-token"] = csrf_token
        stores_req = session.post(
            "https://vh80n2gxi9.execute-api.us-east-1.amazonaws.com/pro/api/stores/list",
            headers=headers,
            data=data,
        )
        stores = json.loads(stores_req.text)["data"]
        for store in stores:
            store_number = store["storeCode"]
            locator_domain = website
            location_name = store["storeName"]
            page_url = search_url
            raw_address = store["address"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "PE"
            phone = store.get("phone", "<MISSING>")

            location_type = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longtitude"]

            hours_of_operation = "<MISSING>"

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
