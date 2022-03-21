# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "ichibanya.co.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "tenpo.ichibanya.co.jp",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cookie": "_ga=GA1.3.1533388763.1639054156; _ga=GA1.4.1533388763.1639054156",
}

params = (
    (
        "f",
        '["\u55B6\u696D\u6642\u9593(From)","\u55B6\u696D\u6642\u9593(To)","\u5B9A\u4F11\u65E5","TEL"]',
    ),
)


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        API_URLs = [
            "https://tenpo.ichibanya.co.jp/api/search",
            "https://worldwide.ichibanya.co.jp/api/search",
        ]
        for search_url in API_URLs:
            log.info(search_url)
            stores_req = session.get(
                search_url,
                headers=headers,
                params=params,
            )

            stores = json.loads(stores_req.text)
            for store in stores:
                store_number = store["key"]
                locator_domain = website
                page_url = search_url.replace("/api/search", "").strip()
                if "tenpo." in page_url:
                    page_url = "https://tenpo.ichibanya.co.jp/map/" + store_number
                else:
                    page_url = (
                        "https://worldwide.ichibanya.co.jp/map/#"
                        + store.get("area2", "").strip()
                    )
                location_name = store["name"]
                raw_address = store.get("address", "<MISSING>")

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address:
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                else:
                    if formatted_addr.street_address_2:
                        street_address = formatted_addr.street_address_2

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                if zip:
                    if not zip.isdigit():
                        zip = "<MISSING>"

                country_code = formatted_addr.country

                phone = store.get("TEL", "<MISSING>")
                location_type = "<MISSING>"

                latitude = store.get("latitude", "<MISSING>")
                longitude = store.get("longitude", "<MISSING>")

                hours_of_operation = ""
                for key in store.keys():
                    if "(From)" in key:
                        if store.get(key, None):
                            hours_of_operation = store.get(key, "")

                    if "(To)" in key:
                        if store.get(key, None):
                            hours_of_operation = (
                                hours_of_operation + " - " + store.get(key, "")
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
