# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gianttiger.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.gianttiger.com",
    "x-vol-master-catalog": "2",
    "x-vol-currency": "CAD",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "x-vol-locale": "en-CA",
    "content-type": "application/json",
    "x-vol-site": "48067",
    "accept": "application/json",
    "x-vol-tenant": "29098",
    "x-vol-catalog": "2",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.gianttiger.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        session.get("https://www.gianttiger.com/", headers=headers)
        stores_req = session.get(
            "https://www.gianttiger.com/api/commerce/storefront/locationUsageTypes/SP/locations/?pageSize=1000",
            headers=headers,
        )
        stores = json.loads(stores_req.text)["items"]

        for store in stores:
            locator_domain = website

            location_name = store["name"]
            street_address = store["address"]["address1"]
            city = store["address"]["cityOrTown"]
            state = store["address"]["stateOrProvince"]
            zip = store["address"]["postalOrZipCode"]

            country_code = store["address"]["countryCode"]
            store_number = store["code"]
            page_url = "https://www.gianttiger.com/store-details?code=" + str(
                store_number
            )

            phone = store["phone"]
            location_type = store["locationTypes"][0]["name"]
            latitude = store["geo"]["lat"]
            longitude = store["geo"]["lng"]

            hours_list = []
            hours_dict = store["regularHours"]
            for day, hours in hours_dict.items():
                if day != "timeZone":
                    if store["regularHours"][day]["isClosed"]:
                        hours_list.append(day + ": Closed")
                    else:
                        hours_list.append(
                            day + ": " + store["regularHours"][day]["label"]
                        )

            hours_of_operation = "; ".join(hours_list).strip()
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
