# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "10fitness.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://10fitness.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = list(
        set(
            stores_sel.xpath(
                '//li[contains(@class,"menu")]/a[contains(@href,"/locations/")]/@href'
            )
        )
    )

    for store_url in stores:
        if store_url == "https://10fitness.com/locations/":
            continue
        page_url = store_url
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(
            store_sel.xpath(
                '//div[@class="et_pb_module et_pb_text et_pb_text_3  et_pb_text_align_left et_pb_bg_layout_light"]/div/h4/text()'
            )
        ).strip()
        if len(location_name) <= 0:
            location_name = "".join(
                store_sel.xpath(
                    '//div[@class="et_pb_module et_pb_text et_pb_text_4  et_pb_text_align_left et_pb_bg_layout_light"]/div/h4/text()'
                )
            ).strip()

        location_name = (
            location_name.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        address = ",".join(
            store_sel.xpath(
                '//div[@class="et_pb_module et_pb_text et_pb_text_3  et_pb_text_align_left et_pb_bg_layout_light"]/div/p//text()'
            )
        ).strip()
        if len(address) <= 0:
            address = ",".join(
                store_sel.xpath(
                    '//div[@class="et_pb_module et_pb_text et_pb_text_4  et_pb_text_align_left et_pb_bg_layout_light"]/div/p//text()'
                )
            ).strip()
        temp_address = address.split(",")
        add_list = []
        for temp in temp_address:
            if len("".join(temp).strip()) > 0:
                add_list.append("".join(temp).strip())

        raw_address = ", ".join(add_list)
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"
        phone = "".join(
            store_sel.xpath('//div[@class="et_pb_blurb_description"]/p/a/text()')
        ).strip()
        if len(phone) <= 0:
            phone = "".join(
                store_sel.xpath('//div[@class="et_pb_blurb_description"]//text()')
            ).strip()

        hours_of_operation = "".join(
            store_sel.xpath(
                '//div[@class="et_pb_module et_pb_text et_pb_text_4  et_pb_text_align_left et_pb_bg_layout_light"]/div/p[1]/text()'
            )
        ).strip()
        if len(hours_of_operation) <= 0:
            hours_of_operation = "".join(
                store_sel.xpath(
                    '//div[@class="et_pb_module et_pb_text et_pb_text_5  et_pb_text_align_left et_pb_bg_layout_light"]/div/p[1]/text()'
                )
            ).strip()

        hours_of_operation = (
            hours_of_operation.encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        if "Open with" in hours_of_operation:
            hours_of_operation = "<MISSING>"

        store_number = "<MISSING>"

        latitude = "".join(
            store_sel.xpath('//div[@class="et_pb_map_pin"]/@data-lat')
        ).strip()
        longitude = "".join(
            store_sel.xpath('//div[@class="et_pb_map_pin"]/@data-lng')
        ).strip()

        if len(latitude) <= 0:
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
