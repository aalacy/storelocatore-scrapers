# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cosbar.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://www.cosbar.com/store-locator/"
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            "{"
            + stores_req.text.split("jsonLocations:{")[1]
            .strip()
            .split("imageLocations")[0]
            .strip()[:-1]
        )["items"]

        for store in stores:
            page_url = "https://www.cosbar.com/store-locator/" + store["url_key"]

            locator_domain = website
            location_name = store["name"]
            street_address = store["address"]
            city = store["city"]
            zip = store["zip"]

            state = (
                store["store_list_html"]
                .split("State:")[1]
                .strip()
                .split("<")[0]
                .strip()
            )
            country_code = store["country"]

            store_number = str(store["id"])
            phone = store["phone"]

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            hour_list = []
            hours = json.loads(store["schedule_string"].replace('"', '"'))
            for day in hours.keys():
                if hours[day][day + "_status"] == "1":
                    time = (
                        hours[day]["from"]["hours"]
                        + ":"
                        + hours[day]["from"]["minutes"]
                        + "-"
                        + hours[day]["to"]["hours"]
                        + ":"
                        + hours[day]["to"]["minutes"]
                    )
                elif hours[day][day + "_status"] == "0":
                    time = "Closed"

                hour_list.append(day + ":" + time)

            hours_of_operation = ";".join(hour_list).strip()

            latitude = store["lat"]
            longitude = store["lng"]

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
