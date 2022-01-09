# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "pizzahut.ru"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    cities_url = (
        "https://spb.pizzahut.ru/cities?_token=n5LUtzAr2xSQB2ZcY255LzdTQxMJTR3YGA05oG85"
    )
    cities_json = json.loads(session.get(cities_url).text)["data"]
    for selected_city in cities_json:
        city_id = selected_city["id"]
        search_url = f"https://pizzahut.ru/restaurant/objects?city_id={city_id}&allow_choose_rest=1&display_all=1"
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)["data"]["restaurants"]
        for store in stores:

            page_url = "<MISSING>"
            location_name = store["name"]
            location_type = "<MISSING>"
            locator_domain = website

            street_address = store["address"]
            city = selected_city["name"]
            state = store["metro"]
            zip = "<MISSING>"

            country_code = "RU"
            store_number = store["id"]
            store_sel = lxml.html.fromstring(store["content"])
            phone = "+7 (800) 100 19 58"
            hours_of_operation = ": ".join(
                store_sel.xpath(
                    '//div[@class="map-tooltip__worktime-item"]/span/text()'
                )
            ).strip()

            latitude = store["coords"][0]
            longitude = store["coords"][1]

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
