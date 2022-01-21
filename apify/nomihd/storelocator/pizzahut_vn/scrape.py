# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "pizzahut.vn"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Project_ID": "WEB",
    "sec-ch-ua-mobile": "?0",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "LANG": "en",
    "Origin": "https://pizzahut.vn",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://pizzahut.vn/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    id_list = ["1", "2", "3"]
    for ID in id_list:
        page_url = "<MISSING>"
        if ID == "1":
            page_url = "https://pizzahut.vn/StoreLocation?area=south"
        if ID == "2":
            page_url = "https://pizzahut.vn/StoreLocation?area=central"
        if ID == "3":
            page_url = "https://pizzahut.vn/StoreLocation?area=north"

        data = {"Area_ID": ID}

        stores_req = session.post(
            "https://api.pizzahut.vn/PZH_MIDDLEWARE_API/store/StoreByArea",
            headers=headers,
            data=json.dumps(data),
        )
        stores = json.loads(stores_req.text)["StoreByArea"]["StoreInfor"]
        for store in stores:

            locator_domain = website

            location_name = store["Store_Name_EN"]

            raw_address = store["adress_desc_EN"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            state = "<MISSING>"
            city = "<MISSING>"
            try:
                city = store["city_en"]
            except:
                city = formatted_addr.city

            if city and city.isdigit():
                city = formatted_addr.city

            try:
                state = store["area_en"]
            except:
                state = formatted_addr.state

            zip = "<MISSING>"

            country_code = "VN"

            phone = store["contact_phone"]
            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
