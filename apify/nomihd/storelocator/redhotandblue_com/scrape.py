# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "redhotandblue.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.redhotandblue.com/locations/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores_list = search_sel.xpath('//div[@id="locations"]')
        if len(stores_list) > 0:
            stores_list = stores_list[0].xpath(".//a/@href")

        for store in stores_list:

            page_url = store.strip()
            locator_domain = website
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)

            location_name = (
                "".join(page_sel.xpath("//title/text()")).strip().split("—")[0].strip()
            )

            street_address = "".join(
                page_sel.xpath(
                    '//div[contains(@class,"et_pb_text_inner") and .//strong]/text()'
                )
            ).strip()
            if len(street_address) <= 0:
                street_address = "".join(
                    page_sel.xpath(
                        '//div[contains(@class,"et_pb_text_inner") and .//strong]/p/text()'
                    )
                ).strip()
            city = location_name.split(",")[0].strip()

            state = location_name.split(",")[-1].strip()
            zip = "<MISSING>"

            country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(
                page_sel.xpath("//strong/a[contains(@href,'tel:')]//text()")
            ).strip()

            location_type = "<MISSING>"

            hours_info = page_sel.xpath(
                '//div[./div[text()="Hours of operation"]]/following-sibling::div'
            )
            hours_list = []
            for hour in hours_info:
                if "Dine-In Menu" not in "".join(hour.xpath(".//text()")).strip():
                    hours_list.append(" ".join(hour.xpath(".//text()")).strip())

            hours_of_operation = "; ".join(hours_list).strip()
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
