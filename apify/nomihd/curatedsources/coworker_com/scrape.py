# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

website = "coworker.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    # Your scraper here

    search_url = "https://www.coworker.com/office-space/cities"

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(search_url)
        time.sleep(10)
        search_sel = lxml.html.fromstring(driver.page_source)

        cities = search_sel.xpath(
            '//div[@class="col-xs-12 pade_none around_city_con"]//ul/li/a'
        )

        for no, _city in enumerate(cities, 1):

            locator_domain = website

            city_url = "".join(_city.xpath("./@href")).strip()
            city = "".join(_city.xpath(".//text()")).strip()

            is_city_req_timeout = True
            while is_city_req_timeout is True:
                try:
                    log.info(city_url)
                    driver.get(city_url)
                    is_city_req_timeout = False
                except:
                    pass

            city_sel = lxml.html.fromstring(driver.page_source)

            stores = city_sel.xpath('//div[@class="item"]//a')

            for n, store in enumerate(stores, 1):

                page_url = "".join(store.xpath("./@href"))

                is_timeout = True
                while is_timeout is True:
                    try:
                        log.info(page_url)
                        driver.get(page_url)
                        is_timeout = False
                    except:
                        pass
                store_sel = lxml.html.fromstring(driver.page_source)

                location_name = " ".join(store.xpath(".//h4//text()")).strip()

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[@id="location"]//h2/span//text()'
                            )
                        ],
                    )
                )

                raw_address = ", ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address:
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                else:
                    if formatted_addr.street_address_2:
                        street_address = formatted_addr.street_address_2

                city = page_url.split("/")[-2]
                state = formatted_addr.state

                zip = formatted_addr.postcode

                country_code = page_url.split("/")[-3]
                phone = "<MISSING>"

                hours = store_sel.xpath('//h4[text()="Opening Hours"]/../div')
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("span/text()")).strip()
                    tim = "".join(hour.xpath("text()")).strip()
                    hours_list.append(day + ":" + tim)

                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .replace("day; ", "day: ")
                    .replace("Show More", "")
                    .strip("; ")
                )

                store_number = "<MISSING>"

                latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.PageUrlId,
            duplicate_streak_failure_factor=-1,
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
