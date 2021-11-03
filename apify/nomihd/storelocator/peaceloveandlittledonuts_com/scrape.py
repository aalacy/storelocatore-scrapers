# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser


website = "peaceloveandlittledonuts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.peaceloveandlittledonuts.com"

    search_url = "https://www.peaceloveandlittledonuts.com/locations"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    states_list = search_sel.xpath('//div[@role="listitem"]/a/@href')

    for state in states_list:
        if base not in state:
            state = base + state
        log.info(state)
        state_res = session.get(state, headers=headers)
        state_sel = lxml.html.fromstring(state_res.text)

        stores_list = state_sel.xpath('//div[@role="listitem"]/a/@href')
        state_name = "".join(
            state_sel.xpath('//div[@class="chalkboard-title"]/text()')
        ).strip()

        for store in stores_list:
            if base not in store:
                store = base + store
            log.info(store)
            store_res = session.get(store, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            page_url = store
            locator_domain = website

            location_name = "".join(
                store_sel.xpath('//div[@class="chalkboard-title"]/text()')
            ).strip()

            raw_address = " ".join(
                store_sel.xpath(
                    '//div[contains(text(),"Address")]/following-sibling::a/text()'
                )
            ).strip()

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = state_name
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath(
                    '//div[contains(text(),"Address")]/preceding-sibling::a/text()'
                )
            )

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
