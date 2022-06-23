# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "espressovivace.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://espressovivace.com/retail"
    with SgRequests(verify_ssl=False) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="loc_col col1of3 column left"]//a/@href'
        )
        for store_url in stores:
            page_url = "https://espressovivace.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website

            location_name = "".join(
                store_sel.xpath("//div[@id='content']/h2/text()")
            ).strip()

            raw_info = store_sel.xpath(
                '//div[@id="content"]/p[./a[contains(text(),"Map")]]/text()'
            )

            raw_list = []
            for index in range(0, len(raw_info)):
                if len("".join(raw_info[index]).strip()) > 0:
                    raw_list.append("".join(raw_info[index]).strip())

            raw_address = ", ".join(raw_list).strip()
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"

            phone = (
                "".join(
                    store_sel.xpath(
                        '//div[@id="content"]/p[contains(text(),"Phone:")]/text()'
                    )
                )
                .strip()
                .replace("Phone:", "")
                .strip()
            )

            location_type = "<MISSING>"
            hours_of_operation = "; ".join(
                store_sel.xpath('//div[@id="content"]/p/strong/text()')
            ).strip()

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = "".join(
                store_sel.xpath(
                    '//div[@id="content"]/p/a[contains(text(),"Map")]/@href'
                )
            ).strip()

            if len(map_link) > 0:
                if "sll=" in map_link:
                    latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
                    longitude = (
                        map_link.split("sll=")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split("&")[0]
                        .strip()
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
