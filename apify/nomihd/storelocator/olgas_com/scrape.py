# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "olgas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "order.olgas.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "x-olo-request": "1",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "application/json, */*",
    "x-requested-with": "XMLHttpRequest",
    "x-olo-app-platform": "web",
    "__requestverificationtoken": "",
    "x-olo-viewport": "Desktop",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.olgas.com/wp-admin/admin-ajax.php?action=store_search&lat=42.36837&lng=-83.35271&max_results=50000&radius=50000&autoload=1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = store["url"]
        locator_domain = website
        location_name = store["store"].replace("&#8211;", "-").strip()

        street_address = store["address"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        street_address = street_address.replace("Breeze Dining Court,", "").strip()
        if "Online Only" in street_address:
            continue

        city = store["city"]
        state = store["state"]
        zip = store["zip"]

        country_code = store["country"]

        store_number = str(store["id"])
        phone = store["phone"]

        location_type = "<MISSING>"
        hours_list = []
        if (
            store["store_time_weekdays"] is not None
            and len(store["store_time_weekdays"]) > 0
        ):
            hours_list.append("Mon-Sat:" + store["store_time_weekdays"])

        if (
            store["store_time_weekend"] is not None
            and len(store["store_time_weekend"]) > 0
        ):
            hours_list.append("Sun:" + store["store_time_weekend"])

        hours_of_operation = ""
        if len(hours_list) > 0:
            hours_of_operation = "; ".join(hours_list).strip()
        else:
            if len(page_url) > 0:
                log.info(page_url)
                if "/menu/" not in page_url:
                    continue
                store_req = session.get(
                    "https://order.olgas.com/api/vendors/"
                    + page_url.split("/menu/")[1].strip(),
                    headers=headers,
                )
                if "vendor" in store_req.text:
                    hours_sections = json.loads(store_req.text)["vendor"][
                        "weeklySchedule"
                    ]["calendars"]
                    for sec in hours_sections:
                        if "Business" == sec["scheduleDescription"]:
                            hours = sec["schedule"]
                            for hour in hours:
                                day = hour["weekDay"]
                                time = hour["description"]
                                hours_list.append(day + ":" + time)

                            break

                    hours_of_operation = "; ".join(hours_list).strip()

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
