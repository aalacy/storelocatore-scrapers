# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "edseasydiner.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://edseasydiner.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//a[@class="a--subtle"]/@href')
    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_type = ""
        if "we are now closed" in store_req.text.lower():
            location_type = "Temporary Closed"

        location_name = "".join(
            store_sel.xpath('//header/h1[@class="title-1"]/text()')
        ).strip()

        locator_domain = website

        raw_info = store_sel.xpath('//div[@class="infobox__content"]/div/p[1]/text()')
        add_list = []
        for add in raw_info:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        raw_address = " ".join(add_list).strip()
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = "GB"

        phone = "".join(store_sel.xpath('//a[contains(@href,"tel:")]/text()')).strip()

        days = store_sel.xpath(
            '//dl[@class="opening-times push visible-inline-block visible--tablet text-align--left"]/dt/text()'
        )
        time = store_sel.xpath(
            '//dl[@class="opening-times push visible-inline-block visible--tablet text-align--left"]/dd/text()'
        )
        hours_list = []
        for index in range(0, len(days)):
            hours_list.append(
                "".join(days[index]).strip()
                + "".join("".join(time[index]).strip().split("\n"))
            )

        hours_of_operation = (
            "; ".join(hours_list)
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
