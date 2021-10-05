# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import json

website = "premierparking.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.premierparking.com/where-we-are-2/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        states_req = session.get(search_url, headers=headers)
        states_sel = lxml.html.fromstring(states_req.text)
        states = states_sel.xpath(
            '//li[./a[contains(text(),"Where We Are")]]/ul/li/a/@href'
        )
        for state_url in states:
            log.info(state_url)
            stores_req = session.get(state_url, headers=headers)
            stores = json.loads(
                stores_req.text.split('"places":')[1]
                .strip()
                .split(',"listing"')[0]
                .strip()
                .split(',"styles"')[0]
                .strip()
            )

            for store in stores:
                page_url = state_url
                locator_domain = website
                location_name = store["title"]

                phone = "<MISSING>"
                raw_address = store["address"].replace(", United States", "").strip()
                formatted_addr = parser.parse_address_usa(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                try:
                    city = store["location"]["city"]
                    if not city:
                        city = formatted_addr.city
                except:
                    city = formatted_addr.city
                    pass
                try:
                    state = store["location"]["state"]
                    if not state:
                        state = formatted_addr.state
                except:
                    state = formatted_addr.state

                try:
                    zip = store["location"]["postal_code"]
                    if not zip:
                        zip = formatted_addr.postcode
                except:
                    zip = formatted_addr.postcode

                country_code = "US"

                store_number = store["id"]
                location_type = "<MISSING>"
                hours_of_operation = "<MISSING>"
                latitude = store["location"]["lat"]
                longitude = store["location"]["lng"]

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
