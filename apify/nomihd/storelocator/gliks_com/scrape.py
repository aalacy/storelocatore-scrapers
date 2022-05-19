# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gliks.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "stockist.co",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-dest": "script",
    "referer": "https://www.gliks.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "if-modified-since": "Sat, 25 Sep 2021 13:18:13 GMT",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://stockist.co/api/v1/u9151/locations/all.js"
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)
        for store_json in stores:
            page_url = "<MISSING>"
            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

            location_name = store_json["name"]

            locator_domain = website

            location_type = "<MISSING>"
            if "Temporarily Closed" in store_json["description"]:
                location_type = "Temporarily Closed"

            street_address = store_json["address_line_1"]
            if store_json["address_line_2"]:
                street_address = street_address + ", " + store_json["address_line_2"]

            city = store_json["city"]
            state = store_json["state"]
            zip = store_json["postal_code"]
            country_code = "US"
            phone = store_json["phone"]
            hours_list = []
            if store_json["description"] and len(store_json["description"]) > 0:
                hours_sel = lxml.html.fromstring(store_json["description"])
                hours_list = hours_sel.xpath(".//text()")

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("day; :", "day:")
                .strip()
                .split("; Shop Type")[0]
                .strip()
                .split("; Temporarily Closed")[0]
                .strip()
                .split("; Shop with")[0]
                .strip()
            )

            store_number = store_json["id"]
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
