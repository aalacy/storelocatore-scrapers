# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "fiat.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Content-Length": "0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://ticariform.fiat.com.tr",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://ticariform.fiat.com.tr/api/Ajax/GetCitiesForMap"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        cities = json.loads(search_res.text.strip(), strict=False)
        for city in cities:
            AreaCode = city["id"]
            params = (
                ("cityId", AreaCode),
                ("districtId", "-1"),
                ("dealertype", "satis"),
            )
            log.info(f"fetching data for areacode#: {AreaCode}")
            stores_req = session.get(
                "https://ticariform.fiat.com.tr/api/Ajax/GetDealersForMap/",
                headers=headers,
                params=params,
            )

            stores = json.loads(stores_req.text)

            for store in stores:
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["dealerName"]

                street_address = store["address"]
                city = store["city"]
                state = store["district"]
                zip = "<MISSING>"

                country_code = "TR"

                phone = store["phone1"]
                store_number = store["dealerCode"]
                if not store_number:
                    store_number = store["id"]

                location_type = store["dealerType"]

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
