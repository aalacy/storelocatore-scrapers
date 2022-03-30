# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "tempo.se"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.tempo.se/butiker-och-oppettider/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            stores_req.text.split("createMap(")[1].strip().split("}],")[0].strip()
            + "}]"
        )
        print(len(stores))
        for store in stores:

            store_number = store["StoreId"]
            API_URL = f"https://www.tempo.se/MapPage/GetStore/{store_number}"
            log.info(API_URL)
            store_req = session.get(API_URL, headers=headers)
            store_json = store_req.json()

            page_url = store_json["URLSegment"]
            if not page_url:
                page_url = search_url
            else:
                page_url = "https://www.tempo.se/butiker-och-oppettider/" + page_url
            locator_domain = website
            location_name = store_json["StoreName"]
            street_address = store_json.get("Street", "<MISSING>")
            city = store_json.get("City", "<MISSING>")
            state = "<MISSING>"
            zip = store_json.get("Zip", "<MISSING>")
            country_code = "SE"

            phone = store_json.get("Phone", "<MISSING>")
            location_type = store_json["StoreServices"]
            if location_type:
                location_type = ", ".join(location_type).strip()
            hours = store_json.get("OpenHours", [])
            hours_list = []
            for hour in hours:
                day = hour["Weekday"]
                time = hour["OpeningHour"] + " - " + hour["ClosingHour"]

                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = (
                store["Lat"],
                store["Lon"],
            )

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
