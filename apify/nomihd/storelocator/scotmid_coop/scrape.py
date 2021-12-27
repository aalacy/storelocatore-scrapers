# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "scotmid.coop"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://scotmid.coop/store-locator/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://scotmid.coop/store/"
        stores_req = session.get(
            search_url,
            headers=headers,
        )

        stores = json.loads(stores_req.text)
        for store in stores:
            if store["type"] != "Scotmid":
                continue
            page_url = "https://scotmid.coop/store/" + store["slug"]
            locator_domain = website
            location_name = "Scotmid " + store["title"]
            street_address = store["address_line_1"]
            city = store["address_line_2"]

            state = store["address_line_3"]
            zip = store["postcode"]
            country_code = "GB"
            phone = store["telephone_number"]

            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_list = []
            if "ot_mon_open" in store and len(store["ot_mon_open"]) > 0:
                hours_list.append(
                    "Mon: " + store["ot_mon_open"] + " - " + store["ot_mon_close"]
                )
            if "ot_tue_open" in store and len(store["ot_tue_open"]) > 0:
                hours_list.append(
                    "Tue: " + store["ot_tue_open"] + " - " + store["ot_tue_close"]
                )
            if "ot_wed_open" in store and len(store["ot_wed_open"]) > 0:
                hours_list.append(
                    "Wed: " + store["ot_wed_open"] + " - " + store["ot_wed_close"]
                )
            if "ot_thu_open" in store and len(store["ot_thu_open"]) > 0:
                hours_list.append(
                    "Thu: " + store["ot_thu_open"] + " - " + store["ot_thu_close"]
                )
            if "ot_fri_open" in store and len(store["ot_fri_open"]) > 0:
                hours_list.append(
                    "Fri: " + store["ot_fri_open"] + " - " + store["ot_fri_close"]
                )
            if "ot_sat_open" in store and len(store["ot_sat_open"]) > 0:
                hours_list.append(
                    "Sat: " + store["ot_sat_open"] + " - " + store["ot_sat_close"]
                )
            if "ot_sun_open" in store and len(store["ot_sun_open"]) > 0:
                hours_list.append(
                    "Sun: " + store["ot_sun_open"] + " - " + store["ot_sun_close"]
                )

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
