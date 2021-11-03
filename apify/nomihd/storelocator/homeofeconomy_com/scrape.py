# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgselenium import SgChrome

website = "homeofeconomy.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    # Your scraper here

    search_url = "https://homeofeconomy.net/"
    search_res = session.get(search_url)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//p[contains(text(),"Honda")]/preceding-sibling::ul/li/a/@href'
    )

    with SgChrome() as driver:

        for store in stores_list:
            driver.get(store)
            page_url = store
            log.info(page_url)
            page_sel = lxml.html.fromstring(driver.page_source)
            locator_domain = website
            json_text = "".join(
                page_sel.xpath('//script[@type="application/ld+json"]/text()')
            )

            json_body = json.loads(json_text)

            location_name = json_body["name"].strip()

            street_address = json_body["address"]["streetAddress"].strip()

            city = json_body["address"]["addressLocality"].strip()
            state = json_body["address"]["addressRegion"].strip()
            zip = json_body["address"]["postalCode"].strip()
            country_code = "US"

            store_number = "<MISSING>"

            phone = json_body["telephone"].strip()

            location_type = "<MISSING>"

            days = {
                "Monday": 0,
                "Tuesday": 1,
                "Wednesday": 2,
                "Thursday": 3,
                "Friday": 4,
                "Saturday": 5,
                "Sunday": 6,
            }
            hours_info = []
            for day, index in days.items():
                if "opens" in json_body["openingHoursSpecification"][index]:
                    opens = json_body["openingHoursSpecification"][index]["opens"]
                    closes = json_body["openingHoursSpecification"][index]["closes"]
                    hours_info.append(f"{day}: {opens} - {closes}")
                else:
                    hours_info.append(f"{day}: Closed")
            hours_of_operation = "; ".join(hours_info)

            latitude = json_body["geo"]["latitude"].strip()
            longitude = json_body["geo"]["longitude"].strip()

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
