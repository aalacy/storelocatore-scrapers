# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gongcha.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (
    ("action", "store_search"),
    ("lat", "20.614465"),
    ("lng", "-103.404944"),
    ("max_results", "25"),
    ("search_radius", "50"),
    ("autoload", "1"),
)


def fetch_data():
    # Your scraper here

    search_url = "https://gongcha.mx/sucursales/"
    api_url = "https://gongcha.mx/wp-admin/admin-ajax.php"
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)

        stores = json.loads(api_res.text)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = store["url"]
            if not page_url:
                page_url = search_url

            location_name = store["store"].strip()

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = (
                store["address"].strip() + ", " + store["address2"].strip()
            ).strip(", ")
            street_address = street_address.split("(")[0].strip()
            city = store["city"]
            state = store["state"]

            zip = "<MISSING>"

            country_code = store["country"]

            phone = store["phone"]
            hour_info = store["hours"]
            hour_sel = lxml.html.fromstring(hour_info)

            hours = list(filter(str, [x.strip() for x in hour_sel.xpath("//text()")]))

            hours_of_operation = (
                "; ".join(hours)
                .replace("es;", "es:")
                .replace("go;", "go:")
                .replace("do;", "do:")
            )

            store_number = store["id"]

            latitude, longitude = store["lat"], store["lng"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
