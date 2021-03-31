# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "pictureshowent.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://pictureshowent.com/theatres/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="theater-page"]//a/@href')
    for store_url in stores:
        page_url = store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//div[contains(@id,"tab-3")]/p/strong[1]/text()')
        ).strip()
        if (
            "Opening"
            in "".join(store_sel.xpath('//h1[@class="title-header"]/text()')).strip()
        ):
            location_type = "Temporary Closed"

        raw_info = store_sel.xpath('//div[contains(@id,"tab-3")]/p/text()')
        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        street_address = raw_list[0].strip()
        city = raw_list[1].split(",")[0].strip()
        state = (
            raw_list[1]
            .split(",")[1]
            .strip()
            .split(" ")[0]
            .strip()
            .replace(".", "")
            .strip()
        )
        zip = raw_list[1].split(",")[1].strip().split(" ")[-1].strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = (
            raw_list[-1]
            .strip()
            .replace("Phone:", "")
            .strip()
            .replace("Office Line:", "")
            .strip()
        )

        hours_of_operation = "<MISSING>"
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"/maps/embed?")]/@src')
        ).strip()
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        else:
            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"/maps?client")]/@src')
            ).strip()
            if "ll=" in map_link:
                latitude = map_link.split("ll=")[1].strip().split(",")[0].strip()
                longitude = (
                    map_link.split("ll=")[1]
                    .strip()
                    .split(",")[1]
                    .strip()
                    .split("&")[0]
                    .strip()
                )
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
