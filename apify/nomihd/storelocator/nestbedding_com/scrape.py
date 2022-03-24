# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "nestbedding.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.nestbedding.com/pages/contact-us"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath('//div[@class="shop"]')

    for store in stores_list:

        page_url = "".join(store.xpath(".//a[@class='shop-detail-link']/@href")).strip()
        if len(page_url) <= 0:
            page_url = "https://www.nestbedding.com/pages/contact-us"

        locator_domain = website

        location_name = "".join(
            store.xpath('.//h3[@class="shop-title"]/text()')
        ).strip()

        raw_address = store.xpath('.//div[@class="shop-info-address-line"]/text()')

        if "Location Closed" in "".join(raw_address).strip():
            continue

        if "Phoenix, AZ" == "".join(raw_address).strip():
            street_address = "<MISSING>"
            city_state = raw_address[0].strip()
            city = city_state.split(",")[0].strip()
            state = city_state.split(",")[-1].strip()
            zip = "<MISSING>"

        else:
            street_address = raw_address[0].strip()
            city_state_zip = raw_address[1].strip()
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            store.xpath('.//div[@class="shop-info-phone-line"]/a/text()')
        ).strip()

        location_type = "<MISSING>"

        hours_list = []
        hours = store.xpath('.//div[@class="shop-info-hours-line"]')

        for hour in hours:
            hour_info = list(filter(str, hour.xpath(".//span//text()")))
            hours_list.append(f"{hour_info[0]}: {hour_info[1]}")

        hours_of_operation = "; ".join(hours_list)

        if hours_of_operation.count("Permanently closed") == 7:
            location_type = "Permanently closed"

        latitude = "".join(store.xpath('.//div[@class="map"]/@data-lat')).strip()
        longitude = "".join(store.xpath('.//div[@class="map"]/@data-long')).strip()

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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
