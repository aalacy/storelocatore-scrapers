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

headers = {
    "authority": "pizzahut.ru",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_urls = ["https://pizzahut.ru/", "https://piter.pizzahut.ru"]
    with SgRequests(verify_ssl=False) as session:
        for search_url in search_urls:
            stores_req = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            json_data = "".join(
                stores_sel.xpath('//script[@id="__NEXT_DATA__"]/text()')
            ).strip()
            stores = json.loads(json_data)["props"]["pageProps"]["initialContext"][
                "restaurants"
            ]
            for store in stores:
                page_url = search_url
                location_name = store["name"]
                location_type = "<MISSING>"
                locator_domain = website

                street_address = store["address"]
                city = store["city"]["name"]
                state = store["metro_station"]
                zip = "<MISSING>"

                country_code = "RU"
                store_number = store["id"]
                phone = store["phone"]
                hours_of_operation = "<MISSING>"
                try:
                    time = store["scheduleActive"][0]["pickup_time"]
                    hours_of_operation = time["from"] + " - " + time["to"]
                except:
                    pass

                latitude = store["map_point"]["latitude"]
                longitude = store["map_point"]["longitude"]

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
