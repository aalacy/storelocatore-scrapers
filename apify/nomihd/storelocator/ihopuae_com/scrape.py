# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "ihopuae.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Referer": "https://ihopuae.com/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://ihopuae.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    token = "".join(stores_sel.xpath('//input[@name="_token"]/@value')).strip()
    cities = json.loads(
        stores_req.text.split("var cityData = ")[1].strip().split("}]};")[0].strip()
        + "}]}"
    )
    for citi in cities.keys():

        stores = cities[citi]
        for store in stores:
            data = {
                "_token": token,
                "select_location_lat": store["lat"],
                "select_location_lng": store["lng"],
                "select_location_urlKey": store["url_key"],
                "select_location_branchId": store["rest_brId"],
                "select_location_min_order": store["min_order"],
                "select_location_delivery_charges": store["delivery_charges"],
                "select_location_max_delivery_time": store["max_delivery_time"],
                "select_location_area": store["area_name"],
                "select_location_city": citi,
            }

            api_req = session.post(
                "https://ihopuae.com/saveCity", headers=headers, data=data
            )
            log.info(
                "fetching info for city: " + store["area_name"].split("|")[0].strip()
            )
            store_sel = lxml.html.fromstring(api_req.text)
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["area_name"].split("|")[0].strip()

            street_address = "<MISSING>"
            city = citi
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "AE"
            store_number = store["id"]
            phone = "".join(
                store_sel.xpath('//div[@class="contact-number"]//text()')
            ).strip()

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]

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
