# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.mideast.jeep.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.mideast.jeep.com/en/find-a-dealer.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        json_str = (
            search_res.text.split('data-component="News" data-props="')[1]
            .split('"></div>')[0]
            .strip()
        )
        json_str = json_str.replace("&#34;", '"')
        json_res = json.loads(json_str)
        stores = json_res["newsData"]["filterableList"]["newsitems"]["newsContent"]

        for idx, store in enumerate(stores, 1):

            locator_domain = website

            location_name = (
                store["bannerDetails"]["title"]["value"].replace("&amp;", "&").strip()
            )
            page_url = search_url
            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = "<MISSING>"

            city = "<MISSING>"

            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = store["bannerDetails"]["preTitle"]["value"]

            phone = (
                store["bannerDetails"]["postTitle"]["value"]
                .split("Phone")[1]
                .split("&amp;lt;/span")[0]
                .strip()
            )

            hours_of_operation = "<MISSING>"

            store_number = "<MISSING>"

            latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PHONE})
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
