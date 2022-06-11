# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "moltonbrown.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.moltonbrown.com/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://api.cxur-kaocorpor1-p3-public.model-t.cc.commerce.ondemand.com/kaowebservices/v2/moltonbrown-us/kao/stores"

    stores_req = session.get(search_url, headers=headers)
    kaoStores = json.loads(stores_req.text)["kaoStores"]
    for kaostr in kaoStores:
        country_code = kaostr["country"]
        store_types = kaostr["stores"]
        for typ in store_types:
            if "Molton Brown Stores" == typ["storeType"]:
                stores = typ["stores"]
                for store in stores:
                    log.info(f"Pulling data for ID: {store}")
                    store_req = session.get(
                        "https://api.cxur-kaocorpor1-p3-public.model-t.cc.commerce.ondemand.com/kaowebservices/v2/moltonbrown-us/stores/"
                        + store,
                        headers=headers,
                    )

                    store_json = json.loads(store_req.text)
                    page_url = (
                        "https://www.moltonbrown.com/store/store-finder/"
                        + store_json["url"]
                    )
                    store_number = "<MISSING>"
                    latitude = store_json["geoPoint"]["latitude"]
                    longitude = store_json["geoPoint"]["longitude"]

                    location_name = store_json["name"]

                    locator_domain = website

                    location_type = store_json["storeType"]

                    street_address = store_json["address"]["line1"]
                    if "line2" in store_json["address"]:
                        if (
                            store_json["address"]["line2"] is not None
                            and len(store_json["address"]["line2"]) > 0
                        ):
                            street_address = (
                                street_address + ", " + store_json["address"]["line2"]
                            )

                    city = store_json["address"].get("town", "<MISSING>")
                    state = "<MISSING>"
                    zip = store_json["address"].get("postalCode", "<MISSING>")
                    phone = store_json["address"].get("phone", "<MISSING>")
                    hours_list = []
                    hours = store_json["kaoOpeningHoursList"]
                    for hour in hours:
                        day = hour["day"]
                        if "openingTime" in hour:
                            time = hour["openingTime"]
                            hours_list.append(day + ":" + time)

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
