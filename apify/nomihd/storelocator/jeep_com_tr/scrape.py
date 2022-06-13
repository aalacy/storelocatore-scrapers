# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "jeep.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://form.jeep.com.tr/bayi-arama?opncl_performance=true&opncl_advertising=true",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://form.jeep.com.tr/api/Ajax/GetAllMapSource"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        stores = json.loads(search_res.text)

        for store in stores:
            page_url = "https://www.jeep.com.tr/yetkili-saticilar"
            locator_domain = website
            location_name = store["dealerName"]

            street_address = store["address"]
            city = store["city"]
            state = store["district"]
            zip = "<MISSING>"

            country_code = "TR"

            phone = store["phone1"]
            if phone:
                phone = phone.split("-")[0].strip()

            store_number = store["dealerCode"]
            if not store_number:
                store_number = store["id"]

            location_type = store["dealerType"]
            if location_type != "satis":
                continue
            hours_of_operation = (
                "Pazartesi – cumartesi 09:00 – 18:00; Pazar 10:00 – 16:00"
            )
            latitude, longitude = store["coordinate"], store["coordinate2"]
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
