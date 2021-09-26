# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from sgselenium.sgselenium import SgChrome

website = "waterstones.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    # Your scraper here
    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        search_url = "https://www.waterstones.com/bookshops/findall"
        driver.get(search_url)
        time.sleep(15)
        stores = json.loads(driver.find_element_by_css_selector("body").text)["data"]
        for store in stores:
            locator_domain = website
            location_name = store["name"]
            page_url = "https://www.waterstones.com" + store["url"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            store_number = store["id"]
            street_address = store["address_1"]
            if store["address_2"] is not None and len(store["address_2"]) > 0:
                street_address = street_address + ", " + store["address_2"]

            city = store["address_3"]
            zip = store["postcode"]
            country_code = "GB"
            state = "<MISSING>"
            phone = store["telephone"]
            location_type = store["closed_message"]
            hours_of_operation = "<MISSING>"

            country_code = "GB"

            if location_type == "":
                location_type = "<MISSING>"
                log.info(page_url)
                driver.get(page_url)
                driver.implicitly_wait(30)
                store_sel = lxml.html.fromstring(driver.page_source)
                hours = store_sel.xpath('//div[@class="opening-times"]/div')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath('.//div[@class="day"]/text()')).strip()
                    _time = "".join(hour.xpath('.//div[@class="times"]/text()')).strip()

                    if len(_time) > 0:
                        day = day.split(" ")[0].strip()
                        hours_list.append(day + ":" + _time)

                hours_of_operation = "; ".join(hours_list).strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
