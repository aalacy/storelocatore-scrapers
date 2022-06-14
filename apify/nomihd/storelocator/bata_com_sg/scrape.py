# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
import json

website = "bata.com.sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.bata.com.sg",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bata.com.sg/pages/store-locator"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        json_list = stores_sel.xpath('//script[@type="application/json"]/text()')
        for js in json_list:
            if "stores" in json.loads(js):
                stores = json.loads(js)["stores"]
                for store in stores:
                    store_number = store["store_id"]
                    page_url = search_url
                    locator_domain = website

                    location_name = store["store_name"]

                    raw_address = store["store_address"]
                    street_address = ", ".join(raw_address.split(",")[:-1]).strip()
                    city = raw_address.split(",")[-1].strip().split(" ")[0].strip()
                    state = "<MISSING>"
                    zip = store["store_zip"]
                    country_code = "SG"
                    phone = store["store_phone"]

                    location_type = "<MISSING>"
                    hours_of_operation = store["store_time"]
                    if hours_of_operation:
                        hours_of_operation = hours_of_operation.replace(
                            "Hours:", ""
                        ).strip()

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

                break


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
