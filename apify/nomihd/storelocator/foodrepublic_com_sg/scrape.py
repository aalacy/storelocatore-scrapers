# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "foodrepublic.com.sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://foodrepublic.com.sg/contact/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="column mcb-column one-third column_info_box location"]'
        )
        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = "".join(
                store.xpath("div[@class='infobox']/h3/text()")
            ).strip()
            raw_address = (
                ", ".join(
                    store.xpath(
                        'div[@class="infobox"]/div[@class="infobox_wrapper"]/table/tr[1]/td[2]/text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            if city and city == "Singapore":
                city = "<MISSING>"

            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "SG"
            store_number = "<MISSING>"
            phone = (
                "".join(
                    store.xpath(
                        'div[@class="infobox"]/div[@class="infobox_wrapper"]//tr[2]/td[2]/text()'
                    )
                )
                .strip()
                .replace("Tel:", "")
                .strip()
            )

            location_type = "<MISSING>"

            hours_of_operation = store.xpath(
                'div[@class="infobox"]/div[@class="infobox_wrapper"]//tr[3]/td[2]/text()'
            )

            if len(hours_of_operation) > 0:
                hours_of_operation = (
                    hours_of_operation[0]
                    .split("*Selected stalls")[0]
                    .strip()
                    .replace("\n", "")
                    .strip()
                )

            latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
