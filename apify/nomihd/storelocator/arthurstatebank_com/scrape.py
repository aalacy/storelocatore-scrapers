# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "arthurstatebank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.arthurstatebank.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="et_pb_main_blurb_image"]/a/@href')
    for store_url in stores:
        page_url = "https://www.arthurstatebank.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath("//div[@class='et_pb_text_inner']/h1/text()")
        ).strip()
        location_type = "Branch"
        locator_domain = website
        raw_info = store_sel.xpath(
            '//div[@class="et_pb_module et_pb_text et_pb_text_1 et_pb_text_align_left et_pb_bg_layout_light"]/div/p/text()'
        )
        phone = raw_info[2].strip().replace("Phone:", "").strip()
        street_address = raw_info[0].strip()
        city = raw_info[1].strip().split(",")[0].strip()
        state = raw_info[1].strip().split(",")[1].strip().split(" ")[0].strip()
        zipp = raw_info[1].strip().split(",")[1].strip().split(" ")[-1].strip()
        hours_of_operation = (
            "; ".join(
                store_sel.xpath(
                    '//div[@class="et_pb_module et_pb_text et_pb_text_3 et_pb_text_align_left et_pb_bg_layout_light"]/div/p[1]/text()'
                )
            )
            .strip()
            .replace(":;", "")
            .strip()
        )
        if "ATM Only:" in "".join(
            store_sel.xpath(
                '//div[@class="et_pb_module et_pb_text et_pb_text_3 et_pb_text_align_left et_pb_bg_layout_light"]/div/p[1]/b/text()'
            )
        ):
            location_type = "ATM Only"

        try:
            hours_of_operation = hours_of_operation.split("; : ;")[0].strip()
        except:
            pass

        country_code = "US"
        store_number = "<MISSING>"

        latitude = ""
        longitude = ""
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
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
            zip_postal=zipp,
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
