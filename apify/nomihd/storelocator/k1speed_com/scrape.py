# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "k1speed.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.k1speed.com/locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//li[@class="menu-item menu-item-type-post_type menu-item-object-page "]/a[contains(@href,"-location.html")]/@href'
    ) + ["https://www.k1speed.com/canovanas-location.html"]

    for store_url in list(set(stores)):
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        if "OPENING SOON" not in "".join(
            store_sel.xpath('//div[@class="wpb_wrapper"]/p/strong/text()')
        ):
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@itemprop="name"]/text()')
            ).strip()
            if location_name == "":
                location_name = "<MISSING>"

            street_address = "".join(
                store_sel.xpath('//span[@itemprop="streetAddress"]/text()')
            ).strip()
            city = "".join(
                store_sel.xpath('//span[@itemprop="addressLocality"]/text()')
            ).strip()
            state = "".join(
                store_sel.xpath('//span[@itemprop="addressRegion"]/text()')
            ).strip()
            zip = "".join(
                store_sel.xpath('//span[@itemprop="postalCode"]/text()')
            ).strip()
            phone_list = store_sel.xpath('//span[@itemprop="telephone"]')
            hours_list = []
            for ph in phone_list:
                hours_list.append("".join(ph.xpath("a/text()")).strip())

            if len(hours_list) > 0:  # It was 0 before
                phone = hours_list[-1].strip()
            else:
                phone = "<MISSING>"

            country_code = "US"
            store_number = "<MISSING>"

            location_type = "<MISSING>"
            if "TEMPORARILY CLOSED" in store_req.text:
                location_type = "TEMPORARILY CLOSED"

            hours_of_operation = "; ".join(
                store_sel.xpath('//time[@itemprop="openingHours"]/@datetime')
            ).strip()

            map_link = "".join(
                store_sel.xpath('//a[@itemprop="address"]/@href')
            ).strip()
            latitude = ""
            longitude = ""
            if len(map_link) > 0:
                if "/@" in map_link:
                    latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                    longitude = map_link.split("/@")[1].strip().split(",")[1].strip()

            if (
                (street_address == "" or street_address == "<MISSING>")
                and (city == "" or city == "<MISSING>")
                and (state == "" or state == "<MISSING>")
                and (zip == "" or zip == "<MISSING>")
                and (latitude == "" or latitude == "<MISSING>")
                and (longitude == "" or longitude == "<MISSING>")
                and (hours_of_operation == "" or hours_of_operation == "<MISSING>")
            ):
                continue

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
