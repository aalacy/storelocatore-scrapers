# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgselenium import SgChrome
import ssl
from sgpostal import sgpostal as parser

ssl._create_default_https_context = ssl._create_unverified_context

website = "witchery.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.witchery.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    # Your scraper here
    search_url = "https://www.witchery.com.au/sitemap"
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(search_url)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath('//section[@class="stores"]//li/a/@href')
        for store_url in stores:
            page_url = "https://www.witchery.com.au" + store_url
            is_timeout = True
            while is_timeout is True:
                try:
                    log.info(page_url)
                    driver.get(page_url)
                    is_timeout = False
                except:
                    pass
            store_sel = lxml.html.fromstring(driver.page_source)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//div[@class="store"]/div[@class="detail"]/h1/text()')
            ).strip()
            if len(location_name) <= 0:
                continue
            log.info(location_name)
            street_Address_list = []
            add_1 = "".join(
                store_sel.xpath(
                    '//div[@class="store"]/div[@class="detail"]//span[@itemprop="streetAddress"]/text()'
                )
            ).strip()
            if len(add_1) > 0:
                street_Address_list.append(add_1)

            add_2 = "".join(
                store_sel.xpath(
                    '//div[@class="store"]/div[@class="detail"]//span[@itemprop="streetAddress2"]/text()'
                )
            ).strip()
            if len(add_2) > 0:
                street_Address_list.append(add_2)

            street_address = ", ".join(street_Address_list).strip()

            raw_address = street_address

            city = "".join(
                store_sel.xpath(
                    '//div[@class="store"]/div[@class="detail"]//span[@itemprop="addressLocality"]/text()'
                )
            ).strip()
            if city:
                raw_address = raw_address + ", " + city

            state = "".join(
                store_sel.xpath(
                    '//div[@class="store"]/div[@class="detail"]//span[@itemprop="addressRegion"]/text()'
                )
            ).strip()

            if state:
                raw_address = raw_address + ", " + state

            zip = "".join(
                store_sel.xpath(
                    '//div[@class="store"]/div[@class="detail"]//span[@itemprop="postalCode"]/text()'
                )
            ).strip()

            if zip:
                raw_address = raw_address + ", " + zip

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

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="store"]/div[@class="detail"]//span[@itemprop="telephone"]/text()'
                )
            ).strip()
            country_code = "AU"
            store_number = "<MISSING>"

            location_type = "<MISSING>"

            latitude = "".join(
                store_sel.xpath(
                    '//div[@class="coordinates"]/meta[@itemprop="latitude"]/@content'
                )
            ).strip()
            longitude = "".join(
                store_sel.xpath(
                    '//div[@class="coordinates"]/meta[@itemprop="longitude"]/@content'
                )
            ).strip()

            hours = store_sel.xpath('//div[@class="opening-hours"]//tr')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if hours_of_operation:
                if hours_of_operation.count("Permanently closed") == 7:
                    continue

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
