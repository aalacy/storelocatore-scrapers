# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import cloudscraper

website = "waterstones.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
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
    with SgRequests(dont_retry_status_codes=set([404])) as session:
        scraper = cloudscraper.create_scraper(sess=session)
        fake_req = scraper.get("https://waterstones.com/", headers=headers)

        search_url = "https://www.waterstones.com/bookshops/findall"
        stores_req = scraper.get(search_url)

        stores = json.loads(stores_req.text)["data"]
        for store in stores:
            locator_domain = website
            location_name = store["name"]
            page_url = "https://www.waterstones.com" + store["url"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            store_number = store["id"]
            street_address = store["address_1"]
            if store["address_2"] is not None and len(store["address_2"]) > 0:
                street_address = street_address + ", " + store["address_2"]

            city = store["address_3"]
            zip = store["postcode"]
            country_code = "GB"
            state = "<MISSING>"
            phone = store["telephone"]
            location_type = store["closed_message"]
            hours_of_operation = "<MISSING>"

            country_code = "GB"

            if location_type == "":
                location_type = "<MISSING>"
                log.info(page_url)
                store_req = scraper.get(page_url)
                store_sel = lxml.html.fromstring(store_req.text)
                hours = store_sel.xpath('//div[@class="opening-times"]/div')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath('.//div[@class="day"]/text()')).strip()
                    time = "".join(hour.xpath('.//div[@class="times"]/text()')).strip()

                    if len(time) > 0:
                        day = day.split(" ")[0].strip()
                        hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

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
