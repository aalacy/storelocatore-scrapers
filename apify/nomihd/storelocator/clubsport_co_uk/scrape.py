# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "clubsport.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.clubsport.co.uk",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.clubsport.co.uk/shoplocal/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        title_list = stores_sel.xpath(
            '//div[contains(@class,"eltd-accordion-holder")]/h4'
        )
        stores = stores_sel.xpath('//div[contains(@class,"eltd-accordion-holder")]/div')
        for index in range(0, len(stores)):

            page_url = "".join(
                stores[index].xpath('.//a[@itemprop="url"]/@href')
            ).strip()
            log.info(page_url)
            locator_domain = website
            location_name = "".join(
                title_list[index].xpath('span[@class="eltd-tab-title"]/text()')
            ).strip()

            raw_address = (
                "".join(
                    stores[index].xpath(
                        './/div[@class="eltd-icon-list-holder "][.//i[@class="eltd-icon-font-awesome fa fa-map-pin "]]/p[@class="eltd-il-text"]/text()'
                    )
                )
                .strip()
                .split(",")
            )
            street_address = ", ".join(raw_address[:-3]).strip()
            city = raw_address[-3].strip()
            state = raw_address[-2].strip()
            zip = raw_address[-1].strip()
            country_code = "GB"

            store_number = "<MISSING>"
            phone = "".join(
                stores[index].xpath(
                    './/div[@class="eltd-icon-list-holder "][.//i[@class="eltd-icon-font-awesome fa fa-phone "]]/p[@class="eltd-il-text"]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = "".join(
                stores[index].xpath(
                    './/div[@class="eltd-icon-list-holder "][.//i[@class="eltd-icon-font-awesome fa fa-table "]]/p[@class="eltd-il-text"]/text()'
                )
            ).strip()
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
