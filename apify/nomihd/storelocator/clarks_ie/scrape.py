# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "clarks.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    sitemap_url = "https://www.clarks.ie/sitemap.xml"
    sitemap_req = session.get(sitemap_url, headers=headers)
    urls = sitemap_req.text.split("<loc>")
    search_url = ""
    for index in range(1, len(urls)):
        url = urls[index].split("</loc>")[0].strip()
        if "Store-en-EUR-" in url:
            search_url = url
            break

    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        page_url = stores[index].split("</loc>")[0].strip()
        log.info(page_url)
        locator_domain = website

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//h1[@class="store-name"]/text()')
        ).strip()

        street_address = "".join(
            store_sel.xpath('//input[@id="storeAddressLine1"]/@value')
        ).strip()

        address_2 = "".join(
            store_sel.xpath('//input[@id="storeAddressLine2"]/@value')
        ).strip()

        if len(address_2) > 0:
            street_address = street_address + ", " + address_2

        city = "".join(store_sel.xpath('//input[@id="city"]/@value')).strip()
        state = "".join(store_sel.xpath('//input[@id="state"]/@value')).strip()
        zip = "".join(store_sel.xpath('//input[@id="postalCode"][1]/@value')).strip()
        country_code = "".join(store_sel.xpath('//input[@id="country"]/@value')).strip()
        store_number = "".join(store_sel.xpath('//input[@id="storeId"]/@value')).strip()

        phone = "".join(store_sel.xpath('//p[@itemprop="telephone"]/text()')).strip()

        location_type = "<MISSING>"
        hours = store_sel.xpath(
            '//div[contains(@class,"booked-details time-listings")]/p[@class="value"]'
        )
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("span[1]/text()")).strip()
            time = "".join(hour.xpath("span[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = ";".join(hours_list).strip()

        latitude = "".join(store_sel.xpath('//input[@id="latitude"]/@value')).strip()
        longitude = "".join(store_sel.xpath('//input[@id="longitude"]/@value')).strip()

        if len(location_name) > 0:
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
