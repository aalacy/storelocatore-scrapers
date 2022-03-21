# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.vaco.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.vaco.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.vaco.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.vaco.com/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {
    "action": "get_initial_location_results_for_map_markers",
    "max_results": "1000",
    "order": "asc",
    "orderby": "title",
    "product": "",
    "retailer": "",
    "address": "",
    "country": "",
    "us_state": "",
}


def fetch_data():
    # Your scraper here
    api_url = "https://www.vaco.com/wp-admin/admin-ajax.php"

    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=data)
        json_res = json.loads(api_res.text)

        stores = json_res["locations"]

        for idx, store in enumerate(stores, 1):

            locator_domain = website

            location_name = store["location_name"].strip()
            page_url = store["location_link"]

            raw_address = "<MISSING>"

            street_address = store["location_street"]
            if "location_street2" in store and store["location_street2"]:
                street_address = (
                    (street_address + ", " + store["location_street2"])
                    .strip()
                    .strip(", ")
                    .strip()
                )

            city = store["location_city"]
            state = store["location_state"]
            if not state:
                if "location_nonUS_region" in store:
                    state = store["location_nonUS_region"]

            zip = store["location_zipcode"]

            country_code = store["location_country_name"]
            phone = store["location_phone"]
            location_type = "<MISSING>"

            store_number = store["location_id"]
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
