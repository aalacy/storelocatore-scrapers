# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

website = "nijiya.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.nijiya.com/store-location"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="store-container holiday"]')
    for store in stores:
        page_url = search_url
        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(store.xpath("p/strong[1]/text()")).strip()
        raw_info = store.xpath("p/text()")
        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        raw_address = ", ".join(raw_list[:-1])
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        if state == "Of Industry":
            city = location_name.replace("STORE", "").strip()
            state = "<MISSING>"

        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        phone = raw_list[-1].strip().replace("TEL-", "").strip()

        sections = store.xpath('div[@style="display:block;"]')
        for section in sections:
            if (
                "Temporary Store Hours"
                in "".join(section.xpath("div/b/text()")).strip()
            ):
                hours_of_operation = (
                    "".join(section.xpath("p/b/text()"))
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                )

        store_number = "<MISSING>"

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
