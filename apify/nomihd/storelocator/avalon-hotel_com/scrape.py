# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "avalon-hotel.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.avalon-hotel.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@id="menu-item-1354"]/ul/li/a/@href')

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath(
                '//footer//div[@class="ftr-credbox__container"]/div[@class="ftr-address"]/h3/text()'
            )
        ).strip()

        add_list = store_sel.xpath(
            '//footer//div[@class="ftr-credbox__container"]/div[@class="ftr-address"]/p/a[1]/text()'
        )
        street_address = "".join(add_list[0]).strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        temp_phone = store_sel.xpath(
            '//footer//div[@class="ftr-credbox__container"]/div[@class="ftr-address"]/p/span/a[contains(@href,"tel:")][1]/text()'
        )

        phone = ""
        if len(temp_phone) > 0:
            phone = temp_phone[0]
        hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath(
                '//footer//div[@class="ftr-credbox__container"]/div[@class="ftr-address"]/p/a[1]/@href'
            )
        ).strip()
        if "/@" in map_link:
            latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
            longitude = map_link.split("/@")[1].strip().split(",")[1]

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
