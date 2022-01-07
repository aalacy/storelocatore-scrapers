# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
import json
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "hamptons.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.hamptons.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.hamptons.co.uk/branches/"
    with SgChrome() as driver:
        with SgRequests(dont_retry_status_codes=([404])) as session:
            stores_req = session.get(search_url, headers=headers)
            stores = json.loads(
                stores_req.text.split("var branchData = ")[1]
                .strip()
                .split("}};")[0]
                .strip()
                + "}}"
            )["branches"]

            for store in stores:

                page_url = "https://www.hamptons.co.uk" + store["branchURL"]
                log.info(page_url)
                driver.get(page_url)
                store_sel = lxml.html.fromstring(driver.page_source)
                locator_domain = website
                location_name = store["name"].strip()

                raw_address = store["address"].replace("\n", ",")

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                if state:
                    if state == "England":
                        state = "<MISSING>"

                zip = formatted_addr.postcode

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
