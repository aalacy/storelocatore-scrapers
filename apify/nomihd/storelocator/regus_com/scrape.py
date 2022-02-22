# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "regus.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.regus.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/json, text/plain, */*",
    "downlink": "1.1",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "viewport-width": "1366",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        api_res = session.get(
            "https://www.regus.com/api/v1/geo-results?lat=37.09024&ws=office-space&lng=-95.712891&gs=true&radius=999999999",
            headers=headers,
        )
        stores = json.loads(api_res.text)
        for store in stores:
            store_info = store["Location"]
            page_url = "https://www.regus.com" + store_info["Url"]
            log.info(page_url)
            API_URL = f"https://ict.infinity-tracking.net/allocate?igrp=5231&ictvid=365c8375-8b48-4475-8783-23cf7a9b6eca&vref=&href={page_url}&state=rlt~1644494770~land~2_48038_direct_b5ad0eca470d1287d7b56c011fc56876&nums=8006334237"
            store_req = session.get(API_URL, headers=headers)
            phone = "<MISSING>"
            hours_of_operation = "Open to members 24h a day"
            if not isinstance(store_req, SgRequestError):
                try:
                    phone = (
                        store_req.text.split('"dynamicNumber":" ')[1]
                        .strip()
                        .split('"')[0]
                        .strip()
                    )
                except:
                    pass

            locator_domain = website
            location_name = store_info["Name"]
            raw_address = store_info["Address"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = formatted_addr.country
            store_number = store_info["ProtonId"]
            location_type = store_info["Brand"]
            latitude = store_info["lat"]
            longitude = store_info["lng"]

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
