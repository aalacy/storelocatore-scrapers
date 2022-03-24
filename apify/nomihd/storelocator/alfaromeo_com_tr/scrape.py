# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "alfaromeo.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.alfaromeo.com.tr",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.alfaromeo.com.tr/bayiler-servisler"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(
            search_res.text.split("SERVİSLER<br><br>")[0].strip()
        )
        tiles = search_sel.xpath('//div[@class="grid-layout-col-4 grid-layout-col"]')

        for tile in tiles:
            stores = tile.xpath('.//div[@class="grid-subtitle"]')
            city = ""
            for store in stores:

                locator_domain = website

                location_name = "".join(store.xpath(".//text()"))
                if not location_name:
                    continue
                page_url = search_url

                location_type = "<MISSING>"
                store_info = store.xpath(
                    './following-sibling::div[@class="grid-text"][1]//text()'
                )
                store_info = list(filter(str, [x.strip() for x in store_info]))[:-1]

                raw_address = store_info[1].strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                temp_city = "".join(
                    store.xpath(
                        "./preceding-sibling::div[@class='grid-title'][1]/text()"
                    )
                ).strip()
                if len(temp_city) > 0:
                    city = temp_city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "TR"
                phone = store_info[3].strip()

                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

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
