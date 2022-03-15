# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "boomersparks.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://boomersparks.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = list(
        set(
            search_sel.xpath(
                '//ul[contains(@class,"menu")]//a[starts-with(@href,"https://boomers")]/@href'
            )
        )
    )

    for store in stores_list:

        page_url = store
        locator_domain = website
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = (
            "".join(page_sel.xpath("//title/text()")).replace(" Home ", "").strip()
        )

        log.info(f"{store}contact/")
        address_res = session.get(f"{store}contact/", headers=headers)
        address_sel = lxml.html.fromstring(address_res.text)

        address_info = list(
            filter(
                str,
                address_sel.xpath(
                    '//h3[contains(text(),"VISIT US")]/following-sibling::p[contains(@class,"description")]//text()'
                ),
            )
        )

        street_address = " ".join(address_info[:-1]).strip()

        city = address_info[-1].split(",")[0].strip()

        state = address_info[-1].split(",")[1].strip().split(" ")[0].strip()
        zip = address_info[-1].split(",")[1].strip().split(" ")[1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            address_sel.xpath(
                '//h3[contains(text(),"CALL AT")]/following-sibling::p[contains(@class,"description")]/a/text()'
            )
        )

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                address_sel.xpath(
                    '//div[contains(@class,"pop-up-body")]//*[contains(text(),"HOURS")]/following::p/text()'
                ),
            )
        )

        if hours:
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())
            hours_of_operation = "; ".join(hours_list)
        else:
            hours = list(
                filter(
                    str,
                    address_sel.xpath(
                        '//div[contains(@class,"pop-up-body")]//*[contains(text(),"OPEN")]/text()'
                    ),
                )
            )

            time = "".join(
                address_sel.xpath('//div[contains(@class,"time-details")]//text()')
            )
            hours_of_operation = f"{hours}: {time}"

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
