# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "craftwarehouse.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://craftwarehouse.com/craft-warehouse-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="col content-box-wrapper content-wrapper-background content-wrapper-boxed link-area-link-icon link-type-text content-icon-wrapper-yes icon-wrapper-hover-animation-pulsate fusion-animated"]'
    )

    for store in stores:
        page_url = "".join(store.xpath('.//a[@class="heading-link"]/@href')).strip()
        locator_domain = website
        location_name = "".join(
            store.xpath('.//a[@class="heading-link"]/h3/text()')
        ).strip()
        if "ONLINE 24/7" in location_name:
            continue
        address = "".join(
            store.xpath(
                'div[@class="content-container"]//a[contains(@href,"/maps")]/text()'
            )
        ).strip()
        street_address = address.split(",")[0].strip()
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[-1].strip()
        zip = address.split(",")[-1].strip().split(" ")[-1].strip()
        street_address = street_address.replace(city, "").strip()
        country_code = "US"

        phone = (
            "".join(
                store.xpath(
                    'div[@class="content-container"]//a[contains(@href,"tel:")]/text()'
                )
            )
            .strip()
            .replace("Call:", "")
            .strip()
        )
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = (
            "; ".join(
                store.xpath(
                    'div[@class="content-container"]/p[./strong[contains(text(),"STORE HOURS")]]/text()'
                )
            )
            .strip()
            .replace("\n", "")
            .strip()
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store.xpath(
                'div[@class="content-container"]//a[contains(@href,"/maps")]/@href'
            )
        ).strip()
        if len(map_link) > 0:
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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
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
