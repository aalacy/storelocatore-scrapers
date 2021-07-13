# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "redhotandblue.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.redhotandblue.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//p[./a[contains(@href,"https://www.redhotandblue")]]/a/@href'
    )

    for store in stores_list:

        page_url = store
        locator_domain = website
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(page_sel.xpath("//title/text()")).strip()

        address_info = list(
            filter(
                str,
                page_sel.xpath(
                    '//div[contains(@class,"et_pb_text_align_center") and .//h2]//h2[not(./a)]//text()'
                ),
            )
        )

        address_info = list(filter(str, ([x.strip() for x in address_info])))
        street_address = "".join(address_info[0]).strip()

        city = address_info[-1].split(",")[0].strip()

        state = (
            "".join(address_info[-1].split(",")[1:]).strip().split(" ")[0].strip(" ,")
        )
        zip = "".join(address_info[-1].split(",")[1:]).strip().split(" ")[1].strip(" ,")

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            list(
                filter(
                    str,
                    page_sel.xpath("//h2[./a]//text()"),
                )
            )
        ).strip()

        location_type = "<MISSING>"

        hours_info = list(
            filter(
                str,
                page_sel.xpath(
                    '//div[./div/h2[text()="Hours"]]/following-sibling::div[1]/div//text()'
                ),
            )
        )
        hours_of_operation = "; ".join(
            list(filter(str, ([x.strip() for x in hours_info])))
        ).replace(":;", ":")
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        raw_address = "<MISSING>"
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
