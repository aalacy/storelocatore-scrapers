# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "usaverx.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.usaverx.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="blockInnerContent"]/p/strong/a/@href')

    for store_url in stores:
        page_url = "https://www.usaverx.com" + store_url
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//h1[@class="pageTitle"]/text()')
        ).strip()

        phone = ""
        address = []
        hours_of_operation = ""
        sections = store_sel.xpath('//div[@class="itemContent"]')
        for sec in sections:
            if (
                "Contact"
                in "".join(sec.xpath('h2[@class="contentTitle"]/text()')).strip()
            ):
                phone = (
                    "".join(
                        sec.xpath(
                            'div[@class="itemInnerContent"]/ul/li[contains(text(),"Phone")]/text()'
                        )
                    )
                    .strip()
                    .replace("Phone:", "")
                    .strip()
                )
                if len(phone) <= 0:
                    phone = (
                        "".join(
                            sec.xpath(
                                'div[@class="itemInnerContent"]/p[contains(text(),"Phone")]/text()'
                            )
                        )
                        .strip()
                        .replace("Phone:", "")
                        .strip()
                    )

            if (
                "Address"
                in "".join(sec.xpath('h2[@class="contentTitle"]/text()')).strip()
            ):
                address = sec.xpath('div[@class="itemInnerContent"]//text()')

            if (
                "Hours"
                in "".join(sec.xpath('h2[@class="contentTitle"]/text()')).strip()
            ):
                hours_of_operation = "; ".join(
                    sec.xpath('div[@class="itemInnerContent"]//text()')
                ).strip()

        if len(address) == 3:
            street_address = "; ".join(address[:-2]).strip()
            city = address[-2].split(",")[0].strip()
            state = address[-2].split(",")[1].strip()
            zip = address[-1]
        elif len(address) == 2:
            street_address = address[0].strip()
            city = address[-1].split(",")[0].strip()
            state = address[-1].split(",")[1].strip().split(" ")[0].strip()
            zip = address[-1].split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"/maps/embed?")]/@src')
        ).strip()
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
