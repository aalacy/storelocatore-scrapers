# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

website = "tubby.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here
    search_url = "https://www.tubbys.com/locations"
    with SgChrome(is_headless=True) as driver:
        driver.get(search_url)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath('//div[@role="gridcell"]')

        for store in stores:
            page_url = "".join(
                store.xpath('.//a[@style="cursor:pointer"]/@href')[-1]
            ).strip()
            locator_domain = website

            location_name = "".join(store.xpath(".//h2//text()")).strip()

            log.info(page_url)
            driver.get(page_url)
            time.sleep(15)
            store_sel = lxml.html.fromstring(driver.page_source)

            address = store_sel.xpath("//div[@data-packed='false'][1]//text()")
            add_list = []
            for add in address:
                if len("".join(add).strip()) > 0:
                    add_list.append("".join(add).strip())

            street_address = "".join(add_list[0]).strip()
            city = add_list[1]
            state_zip = add_list[2].replace(",", "").strip()
            state = state_zip.split(" ")[0].strip()
            if state == "City":
                state = "MI"
                city = "Imlay City"

            zip = state_zip.split(" ")[-1].strip()
            country_code = "US"

            store_number = page_url.split("-")[-1].strip()
            phone = "".join(
                store.xpath('.//p//a[contains(@href,"tel:")][1]//text()')
            ).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath(
                '//p[@style="font-size:16px; line-height:1.5em;"]/span'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                tim = "".join(hour.xpath("span[2]/text()")).strip()
                hours_list.append(day + tim)

            if len(hours_list) <= 0:
                hours = store_sel.xpath(
                    '//div[@data-packed="true"]/p[@class="font_8" and not(@style)]'
                )
                for hour in hours:
                    hours_list.append("".join(hour.xpath(".//text()")).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("; ; ", "")
                .replace(":;", ":")
                .strip()
                .replace("; AM", "AM;")
                .replace("-;", "-")
                .strip()
                .replace("; -", "-")
                .replace(";;", ";")
                .strip()
                .replace("; PM", "PM")
            )
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
