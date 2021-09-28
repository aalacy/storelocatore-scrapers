# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "artistcraftsman.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/5908/stores.js"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        stores = json.loads(search_res.text)["stores"]

        for store in stores:

            page_url = "https://artistcraftsman.com/find-a-location/"
            locator_domain = website

            location_name = store["name"]

            raw_address = (
                store["address"]
                .replace(", USA", "")
                .strip()
                .replace(", US", "")
                .strip()
                .split(",")
            )
            street_address = (
                ", ".join(raw_address[:-3])
                .strip()
                .replace("Arcade Mall Building <br/>", "")
                .strip()
            )
            city = raw_address[-3].strip()
            state = raw_address[-2].strip()
            zip = raw_address[-1].strip()
            if " " in zip:
                street_address = raw_address[0].strip()
                city = raw_address[-2].strip()
                state = raw_address[-1].strip().split(" ")[0].strip()
                zip = raw_address[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            store_number = store["id"]
            phone = store["phone"]

            location_type = "<MISSING>"

            hours_sel = lxml.html.fromstring(store["description"])
            hours_of_operation = "; ".join(hours_sel.xpath(".//text()")).strip()

            latitude, longitude = store["latitude"], store["longitude"]

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
