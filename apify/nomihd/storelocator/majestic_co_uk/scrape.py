# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "majestic.co.uk"
domain = "https://www.majestic.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.majestic.co.uk/stores"
    home_req = session.get(search_url, headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    regions = home_sel.xpath(
        '//div[@class="LinkButton t-link text-center mb-2 text-left content-wrapper"]/div/a/@href'
    )
    for region_url in regions:
        stores_req = session.get(domain + region_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//span[@class="store-list-buttons"]')
        for store in stores:
            locator_domain = website
            store_data = store.xpath('a[@class="d-inline-block view-on-map"]')[0]
            location_name = "".join(store_data.xpath("@data-name")).strip()
            page_url = domain + "".join(store_data.xpath("@data-id")).strip()
            latitude = "".join(store_data.xpath("@data-lat")).strip()
            longitude = "".join(store_data.xpath("@data-long")).strip()
            store_number = "<MISSING>"
            phone = "".join(store_data.xpath("@data-phone")).strip()

            log.info(page_url)

            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_type = "<MISSING>"
            raw_address = "".join(
                store_sel.xpath('//p[@class="store__address"]/text()')
            ).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            if "temporarily closed" in store_req.text:
                location_type = "temporarily closed"

            if "closed permanently" in store_req.text:
                continue
            hours = store_sel.xpath('//div[@class="store-time-line"]')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('span[@class="store-day"]/text()')).strip()
                time = "".join(
                    hour.xpath(
                        'span[@class="store-day"]/span//span[@class="store-time"]/text()'
                    )
                ).strip()
                if len(time) > 0 and "Bank Holidays" not in day:
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            country_code = "GB"

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
