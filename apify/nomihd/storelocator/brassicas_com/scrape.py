# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "brassicas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://brassicas.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath('//div[contains(@class,"locations")]//li/a/@href')

    for store in stores_list:

        page_url = store
        locator_domain = website
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(page_sel.xpath("//h1/text()")).strip()

        details_info = list(
            filter(
                str,
                page_sel.xpath('//div[@class="copy"]/p//text()'),
            )
        )

        details_info = details_info[1:]

        street_address = details_info[0].strip()

        city = details_info[1].split(",")[0].strip()

        state = details_info[1].split(",")[1].strip().split(" ")[0].strip()
        zip = details_info[1].split(",")[1].strip().split(" ")[1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = details_info[-2].strip()

        location_type = "<MISSING>"

        hours_of_operation = details_info[-1].strip()

        lat_lng_href = "".join(
            page_sel.xpath('//p[contains(.//@href, "maps/")]//@href')
        )

        if "z/data" in lat_lng_href:
            lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
        else:

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
