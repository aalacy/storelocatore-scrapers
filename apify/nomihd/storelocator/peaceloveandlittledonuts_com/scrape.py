# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "peaceloveandlittledonuts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.peaceloveandlittledonuts.com",
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
}


def fetch_data():
    # Your scraper here
    base = "https://www.peaceloveandlittledonuts.com"

    search_url = "https://www.peaceloveandlittledonuts.com/locations"
    with SgRequests() as session:
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
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address:
                    street_address = street_address.replace("Hill Center ", "").strip()
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
