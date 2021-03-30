# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "homebase_co.uk"
domain = "https://www.homebase.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.homebase.co.uk/stores.list"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@class="storesList_locations"]/a/@href')

    for store_url in stores:
        page_url = domain + store_url
        log.info(page_url)
        locator_domain = website
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//h3[@class="storeDetailMap_locationName_title"]/text()')
        ).strip()
        raw_address = (
            "".join(
                store_sel.xpath(
                    '//div[@class="storeDetailMap_address"]/p[@class="storeDetailMap_paragraph"][1]/text()'
                )
            ).strip()
            + "".join(
                store_sel.xpath(
                    '//div[@class="storeDetailMap_address"]/p[@class="storeDetailMap_paragraph"][2]/text()'
                )
            ).strip()
        )

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state

        zip = "".join(
            store_sel.xpath(
                '//div[@class="storeDetailMap_address"]/p[@class="storeDetailMap_paragraph"][3]/text()'
            )
        ).strip()

        country_code = "GB"

        store_number = "<MISSING>"
        phone = "".join(
            store_sel.xpath(
                '//div[@class="storeDetailMap_address"]//a[@class="storeDetailMap_link_text"]/text()'
            )
        ).strip()

        location_type = "<MISSING>"

        latitude = (
            "".join(
                store_sel.xpath(
                    '//h3[@class="storeDetailMap_locationName_title"]/@data-latlong'
                )
            )
            .strip()
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                store_sel.xpath(
                    '//h3[@class="storeDetailMap_locationName_title"]/@data-latlong'
                )
            )
            .strip()
            .split(",")[1]
            .strip()
        )

        hours = store_sel.xpath('//li[@class="storeDetailMap_openingTime_item"]')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("span[1]/text()")).strip()
            time = "".join(hour.xpath("span[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

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
