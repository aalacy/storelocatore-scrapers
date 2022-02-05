# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "splashcarwashes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "splashcarwashes.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://splashcarwashes.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://splashcarwashes.com/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    api_url = "https://splashcarwashes.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=0298e83842&load_all=1&layout=1"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)

        stores = json_res

        for idx, store in enumerate(stores, 1):

            locator_domain = website

            location_name = store["title"].strip()
            page_url = store["website"]

            raw_address = "<MISSING>"

            street_address = store["street"]

            city = store["city"]
            state = store["state"]
            zip = store["postal_code"]

            country_code = store["country"]
            phone = store["phone"]
            location_type = "<MISSING>"

            store_number = store["id"]
            hours = store["open_hours"]
            if hours:
                hour_list = []
                hours = json.loads(hours)
                for day, time in hours.items():
                    hour_list.append(f"{day}: {time[0]}")
                hours_of_operation = "; ".join(hour_list)
            else:
                hours_of_operation = "<MISSING>"

            latitude, longitude = store["lat"], store["lng"]

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
