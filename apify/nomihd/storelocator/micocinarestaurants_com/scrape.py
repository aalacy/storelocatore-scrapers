# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "micocinarestaurants.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.micocina.com/wp-admin/admin-ajax.php"

    data = {
        "action": "get_all_stores",
        "lat": "",
        "lng": "",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)

    for key in stores.keys():
        latitude = stores[key]["lat"]
        longitude = stores[key]["lng"]
        page_url = stores[key]["we"]

        locator_domain = website
        location_name = stores[key]["na"]
        street_address = stores[key]["st"]
        city = stores[key]["ct"]
        state = stores[key]["rg"]
        zip = stores[key]["zp"]
        country_code = "US"
        store_number = stores[key]["ID"]
        location_type = "<MISSING>"

        phone = stores[key]["te"]

        hours_of_operation = "<MISSING>"
        if page_url and len(page_url) > 0:
            page_url = "https://www.micocina.com" + page_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if "Expected to Open" in store_req.text:
                continue
            store_sel = lxml.html.fromstring(store_req.text)
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="fusion-text fusion-text-1"]/p/span[contains(text(),"day ")]/text()'
                        )
                    ],
                )
            )
            log.info(hours)
            hours_of_operation = (
                "; ".join(hours)
                .strip()
                .replace("\n", "")
                .strip()
                .split("Accommodate")[0]
                .strip()
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
