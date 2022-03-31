# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "pizzahut-tt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut-tt.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut-tt.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    search_res = session.get(search_url, headers=headers)
    stores = json.loads(search_res.text)
    for store in stores:

        page_url = "https://www.pizzahut-tt.com/find-a-hut/"
        hours_req = session.get(page_url, headers=headers)
        hours_sel = lxml.html.fromstring(hours_req.text)
        locator_domain = website
        location_name = store["store"]
        street_address = store["address"]
        raw_address = street_address
        city = store["city"]
        if city:
            raw_address = raw_address + ", " + city
            city = city.split(".")[0].strip().split(",")[-1].strip()

        state = store["state"]
        if state:
            raw_address = raw_address + ", " + state
        zip = store["zip"]
        if zip:
            raw_address = raw_address + ", " + zip

        street_address = street_address.replace(location_name + ",", "").strip()
        country_code = store["country"]

        phone = "(868) 225-4488"
        store_number = store["id"]
        location_type = "<MISSING>"
        hours_list = []
        hours = hours_sel.xpath('//ul[@class="find-time"]/li')
        for hour in hours:
            hours_list.append(
                "".join(hour.xpath("text()")).strip().split("except")[0].strip()
            )
        hours_of_operation = "; ".join(hours_list).strip()

        latitude, longitude = store["lat"], store["lng"]

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
