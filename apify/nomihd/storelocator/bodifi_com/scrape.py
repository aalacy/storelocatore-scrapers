# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bodifi.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bodifi.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bodifi.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//li[./a/span[contains(text(),"LOCATIONS")]]/ul/li/a/@href'
    )
    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website

        location_name = "".join(
            store_sel.xpath("//div[@itemprop='text']/h2[1]/text()")
        ).strip()
        add_list = []
        if len(location_name) <= 0:
            location_name = "".join(
                store_sel.xpath(
                    '//div[@class="elementor-column-wrap elementor-element-populated"][./div/div/div/h2[contains(text(),"IDAHO FALLS")]]/div[1]/div[1]/div[1]/h2/text()'
                )
            ).strip()
            add_list = (
                "".join(
                    store_sel.xpath(
                        '//div[@class="elementor-column-wrap elementor-element-populated"][./div/div/div/h2[contains(text(),"IDAHO FALLS")]]/div[1]/div[2]/div[1]/h2/text()'
                    )
                )
                .strip()
                .split(",")
            )
        else:
            add_list = (
                "".join(store_sel.xpath("//div[@itemprop='text']/h2[2]/text()"))
                .strip()
                .split(",")
            )

        street_address = ", ".join(add_list[0:-2]).strip()
        if street_address[-1] == ",":
            street_address = "".join(street_address[:-1]).strip()
        city = add_list[-2].strip()
        state = add_list[-1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(" ")[-1].strip()
        phone = "".join(
            store_sel.xpath(
                '//div[@itemprop="text"]/p/a[contains(@href,"tel")]//text()'
            )
        ).strip()

        if len(phone) <= 0:
            phone = "".join(
                store_sel.xpath('.//a[contains(@href,"tel")]//text()')
            ).strip()
        country_code = "US"
        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
