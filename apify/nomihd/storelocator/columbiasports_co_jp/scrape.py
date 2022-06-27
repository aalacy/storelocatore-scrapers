# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "columbiasports.co.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.columbiasports.co.jp",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(
            "https://www.columbiasports.co.jp/shop/store/list.aspx", headers=headers
        )
        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//li[@class="block-store-list--store"]')

        for store in stores:

            page_url = "".join(store.xpath("a/@href")).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website

            location_name = "".join(
                store.xpath('.//p/span[@class="shop_name"]/text()')
            ).strip()

            raw_address = "".join(
                store_sel.xpath(
                    '//dl[@class="block-store-detail--store-address"]/dd/text()'
                )
            ).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            state = formatted_addr.state
            zip = formatted_addr.postcode

            city = "".join(store.xpath('.//span[@class="shop_area"]/text()')).strip()

            country_code = "JP"

            store_number = page_url.split("/")[-2].strip()
            phone = "".join(
                store_sel.xpath(
                    '//dl[@class="block-store-detail--store-tel"]/dd/text()'
                )
            ).strip()
            location_type = "".join(store.xpath("a/p/span[2]/@class")).strip()
            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                "".join(
                    store_sel.xpath(
                        '//div[@class="block-store-detail--store-map-info"]/input[@id="latitude"]/@value'
                    )
                ).strip(),
                "".join(
                    store_sel.xpath(
                        '//div[@class="block-store-detail--store-map-info"]/input[@id="longitude"]/@value'
                    )
                ).strip(),
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
