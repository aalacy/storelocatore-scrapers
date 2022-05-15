# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import lxml.html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "bridgfords.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bridgfords.co.uk/branches/"

    with SgChrome() as driver:
        with SgRequests(dont_retry_status_codes=([404])) as session:
            search_res = session.get(search_url, headers=headers)
            stores = json.loads(
                search_res.text.split("var branchData = ")[1]
                .strip()
                .split("}};")[0]
                .strip()
                + "}}"
            )["branches"]

            for store in stores:

                page_url = "https://www.bridgfords.co.uk" + store["branchURL"]
                log.info(page_url)
                driver.get(page_url)
                store_sel = lxml.html.fromstring(driver.page_source)
                locator_domain = website
                location_name = store["name"].strip()

                raw_address = store["address"].replace("\n", ",").split(",")
                street_address = ", ".join(raw_address[:-3]).strip()

                city = raw_address[-3].strip()
                state = raw_address[-2].strip()
                zip = raw_address[-1].strip()

                country_code = "GB"

                store_number = store["branchID"]

                phone = store["salesContactNumber"]

                location_type = ""
                if store["salesEnabled"] is True:
                    if store["lettingsEnabled"] is True:
                        location_type = "Sales, Lettings"
                    else:
                        location_type = "Sales"
                else:
                    if store["lettingsEnabled"] is True:
                        location_type = "Lettings"

                hours = store_sel.xpath('//div[@class="card card--office"]')
                hours_list = []
                if len(hours) > 0:
                    hours = hours[0].xpath('.//li[@class="accordion__item-body-item"]')
                    for hour in hours:
                        time = "".join(
                            hour.xpath(
                                './/strong[@class="opening-times__text opening-times__text--time"]/text()'
                            )
                        ).strip()
                        day = "".join(
                            hour.xpath('.//span[@class="opening-times__text"]/text()')
                        ).strip()
                        hours_list.append(day + ": " + time)

                hours_of_operation = "; ".join(hours_list).strip()

                latitude, longitude = store["lat"], store["lng"]

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
