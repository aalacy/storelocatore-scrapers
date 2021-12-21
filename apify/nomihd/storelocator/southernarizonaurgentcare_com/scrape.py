# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "southernarizonaurgentcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://southernarizonaurgentcare.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="location col-12 col-md-6 col-lg-4"]/h4/a/@href'
    )

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="row location-info"]/div[1]/h1/text()')
        ).strip()
        if "Virtual" in location_name:
            continue
        address = store_sel.xpath(
            '//div[@class="row location-info"]/div[1]/p[@class="mt-4"]/text()'
        )
        raw_address = []
        for add in address:
            if len("".join(add).strip()) > 0:
                raw_address.append(
                    "".join(add)
                    .strip()
                    .replace("\r\n", ",")
                    .strip()
                    .replace("\n", ",")
                    .strip()
                )

        formatted_addr = parser.parse_address_usa(", ".join(raw_address))
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"
        phone = ""
        sections = store_sel.xpath('//div[@class="row location-info"]/div[1]/p')
        for section in sections:
            if "fas fa-phone" in "".join(section.xpath("i/@class")).strip():
                phone = "".join(section.xpath("text()")).strip()

        location_type = "<MISSING>"

        hours_of_operation = (
            ":".join(
                store_sel.xpath(
                    '//div[@class="row location-info"]/div[1]/h5[@class="mb-3"]/text()'
                )
            )
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        latitude = ""
        longitude = ""
        if "latlong = " in store_req.text:
            latitude = (
                store_req.text.split("latlong = ")[1]
                .strip()
                .split(",")[0]
                .strip()
                .replace('"', "")
                .strip()
            )
            longitude = (
                store_req.text.split("latlong = ")[1]
                .strip()
                .split(",")[1]
                .strip()
                .replace('"', "")
                .strip()
            )

            if ".split('" in latitude:
                latitude = "<MISSING>"

            if "')" in longitude:
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
