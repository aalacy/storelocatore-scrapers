# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "rush.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.rush.co.uk/salon-finder"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//li[@class="accordion__item"]/a/@href')
        for store_url in stores:
            page_url = store_url
            log.info(store_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@itemprop="name"]/text()')
            ).strip()

            if location_name == "":
                location_name = "<MISSING>"

            raw_address = store_sel.xpath('//address[@class="sidebar__address"]')
            if len(raw_address) > 0:
                temp_add = raw_address[0].xpath(".//text()")
                add_list = []
                for temp in temp_add:
                    if len("".join(temp).strip()) > 0:
                        add_list.append("".join(temp).strip())

                raw_address = ", ".join(add_list).strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                if not city:
                    city = location_name.split("Rush")[1].strip()
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = formatted_addr.country

                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="desktop-salon-actions"]//span[@itemprop="telephone"]/text()'
                    )
                ).strip()

                location_type = "<MISSING>"
                store_number = "<MISSING>"
                hours = store_sel.xpath(
                    '//div[@class="salon_mobile_address_hours"]/div[2]//text()'
                )
                hours_list = []
                for hour in hours:
                    if (
                        "mon:" in "".join(hour).strip().lower()
                        or "tue:" in "".join(hour).strip().lower()
                        or "wed:" in "".join(hour).strip().lower()
                        or "thu:" in "".join(hour).strip().lower()
                        or "fri:" in "".join(hour).strip().lower()
                        or "sat:" in "".join(hour).strip().lower()
                        or "sun:" in "".join(hour).strip().lower()
                    ):
                        hours_list.append("".join(hour).strip())

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

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
