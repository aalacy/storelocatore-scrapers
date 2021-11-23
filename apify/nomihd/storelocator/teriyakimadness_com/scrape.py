# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "teriyakimadness.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://teriyakimadness.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//*[contains(@class,"toggle_title")]/following-sibling::div//a[not(contains(@href,"coming"))]/@href'
    )

    for store in stores_list:

        page_url = store
        locator_domain = website
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)
        if not page_res.ok:
            continue

        location_name = "".join(page_sel.xpath("//title/text()")).strip()
        if "MX |" in location_name:
            continue
        raw_address = " ".join(
            list(
                filter(
                    str,
                    page_sel.xpath(
                        '//*[contains(@class,"text") and ./h3]/h3[1]//text()'
                    ),
                )
            )
        )

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        if street_address:
            street_address = street_address.replace("Ste", "Suite")

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = formatted_addr.country

        if not country_code:
            country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(
            page_sel.xpath('//*[contains(@class,"text") and ./h3]/h3[2]//text()')
        )

        location_type = "<MISSING>"
        hours_list = list(
            filter(
                str,
                page_sel.xpath(
                    '//*[contains(@class,"text") and ./h3]/h3[2]/following-sibling::h3//text()'
                ),
            )
        )

        hours_list = list(filter(str, [x.strip() for x in hours_list]))

        hours_of_operation = (
            "; ".join(hours_list)
            .replace("\n", " ")
            .replace("  ", " ")
            .replace("day; ", "day: ")
            .strip(" ;")
        )

        lat_lng_href = "".join(page_sel.xpath('//a[contains(@href,"maps")]/@href'))

        if "z/data" in lat_lng_href:
            lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
        else:

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
