# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "hamptons.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

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
    page_no = 1
    search_url = "https://www.hamptons.co.uk/branches/page-{}/"
    while True:
        log.info(f"pulling links from page:{page_no}")
        stores_req = session.get(search_url.format(str(page_no)), headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="card-grid"]//a[@class="card__link"][not(contains(@href,"card.detailsPageUrl"))]/@href'
        )
        for store_url in stores:
            page_url = "https://www.hamptons.co.uk" + store_url

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@class="hero__title"]/text()')
            ).strip()
            raw_address = "".join(
                store_sel.xpath('//p[@class="hero__text"]/text()')
            ).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            if state:
                if state == "England":
                    state = "<MISSING>"

            zip = formatted_addr.postcode

            country_code = "GB"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="card-content"][./div[@class="card-content__text"]/h4[contains(text(),"Sales")]]//span[@class="branch-contact__telephone-text"]/text()'
                )
            ).strip()
            location_type = "<MISSING>"
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            hours = store_sel.xpath(
                '//div[@class="card-content"][./div[@class="card-content__text"]/h4[contains(text(),"Sales")]]//ul[@class="accordion__item-body-list"]/li'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("span/text()")).strip()
                time = "".join(hour.xpath("strong/text()")).strip()
                hours_list.append(day + ":" + time)

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
                raw_address=raw_address,
            )

        next_page = stores_sel.xpath(
            '//a[./span[contains(text(),"Load more offices")]]/@href'
        )
        if len(next_page) > 0:
            page_no = page_no + 1
        else:
            break


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
