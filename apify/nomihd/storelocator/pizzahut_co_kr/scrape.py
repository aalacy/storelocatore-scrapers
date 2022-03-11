# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import string

website = "pizzahut.co.kr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Accept": "application/json, text/plain, */*",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Origin": "https://www.pizzahut.co.kr",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.pizzahut.co.kr/misc/address",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    alphabets = list(string.ascii_lowercase)
    for alp in alphabets:
        data = {"coordSystem": "UTMK", "query": alp}
        stores_req = session.post(
            "https://www.pizzahut.co.kr/api/gis/address",
            headers=headers,
            data=json.dumps(data),
        )

        stores = json.loads(stores_req.text)
        for store in stores:
            log.info(store["name"])
            locator_domain = website

            location_name = store["name"]

            street_address = store["addressStreet"]

            location_type = "<MISSING>"
            if "예정" in street_address:
                location_type = "Coming Soon"

            street_address = street_address.split("(")[0].strip()

            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "KR"

            phone = "<MISSING>"

            store_number = "<MISSING>"

            page_url = "https://www.pizzahut.co.kr/misc/address"

            hours_of_operation = "<MISSING>"

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
