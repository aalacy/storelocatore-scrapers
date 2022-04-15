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
            locator_domain = website
            location_name = "".join(store.xpath(".//h2//text()")).strip()
            log.info(location_name)
            country_code = "US"
            phone = "".join(
                store.xpath('.//p//a[contains(@href,"tel:")][1]//text()')
            ).strip()
            location_type = "<MISSING>"

            temp_url = store.xpath('.//a[@class="_2wYm8"]/@href')
            if len(temp_url) > 0:
                page_url = "".join(temp_url[-1]).strip()
                store_number = page_url.split("-")[-1].strip()
                add_list = []

                while len(add_list) <= 0:
                    log.info(page_url)
                    try:
                        driver.get(page_url)
                        time.sleep(15)
                        store_sel = lxml.html.fromstring(driver.page_source)

                        temp_addr = store_sel.xpath(
                            "//p[@class='font_8']/span[@style='font-size:17px;']"
                        )
                        if len(temp_addr) > 0:
                            address = temp_addr[0].xpath("span//text()")
                            if len(address) == 1:
                                add_2 = temp_addr[1].xpath("span//text()")
                                if len(add_2) > 0:
                                    address = address + add_2

                            log.info(address)
                        for add in address:
                            if len("".join(add).strip()) > 0:
                                add_list.append("".join(add).strip())
                    except:
                        pass

                street_address = "".join(add_list[0]).strip()
                city = add_list[1]
                try:
                    state_zip = add_list[2].replace(",", "").strip()
                except:
                    pass

                if page_url == "http://tubbys.com/location-page/tubbys-redford-104":
                    state_zip = "MI 48240"

                state = state_zip.split(" ")[0].strip()
                if state == "City":
                    state = "MI"
                    city = "Imlay City"

                zip = state_zip.split(" ")[-1].strip()

                hours = store_sel.xpath(
                    '//p[@style="font-size:16px; line-height:1.5em;"]/span'
                )
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("span[1]//text()")).strip()
                    if len(hour.xpath("span")) == 2:
                        tim = "".join(hour.xpath("span[2]//text()")).strip()
                    elif len(hour.xpath("span")) == 3:
                        tim = "".join(hour.xpath("span[3]//text()")).strip()
                    hours_list.append(day + tim)

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
            else:
                log.info("hahah")
                continue
                store_number = location_name.split(" ")[-1].strip()
                page_url = search_url
                address = store.xpath(".//div[@data-packed='false'][2]//text()")
                raw_info = []
                for add in address:
                    if len("".join(add).strip().replace("\u200b", "").strip()) > 0:
                        raw_info.append("".join(add).strip())

                street_address = "".join(raw_info[0]).strip()
                city = raw_info[1].split(",")[0].strip()
                state = raw_info[1].split(",")[-1].strip().split(" ")[0].strip()
                zip = raw_info[1].split(",")[-1].strip().split(" ")[-1].strip()
                hours_of_operation = "<MISSING>"
                phone = raw_info[-1].strip()

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
