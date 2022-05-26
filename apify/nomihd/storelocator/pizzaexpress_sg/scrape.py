# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzaexpress.sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.pizzaexpress.sg",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://www.pizzaexpress.sg/restaurants/"
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//p[@class="entry-more-link"]/a/@href')
        for store_url in stores:
            page_url = "https://www.pizzaexpress.sg" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = "".join(
                store_sel.xpath('//h1[@data-content-field="title"]//text()')
            ).strip()
            locator_domain = website

            raw_address = store_sel.xpath(
                '//div[@class="sqs-block html-block sqs-block-html"]/div/p[1]/text()'
            )
            if len(raw_address) > 0:
                raw_address = raw_address[0]

            street_address = ", ".join(raw_address.split(",")[:-1]).strip()
            city = "<MISSING>"
            state = "<MISSING>"
            zip = raw_address.split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "SG"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="sqs-block html-block sqs-block-html"]//p[./a[contains(@href,"tel:")]]//text()'
                )
            ).strip()
            location_type = "<MISSING>"

            sections = store_sel.xpath(
                '//div[@class="sqs-block html-block sqs-block-html"]'
            )
            if len(sections) > 0:
                sections = sections[0].xpath('div[1]/p[@style="white-space:pre-wrap;"]')
                if len(sections) > 0:
                    hours_of_operation = "".join(sections[-1].xpath("text()")).strip()

            latitude = "".join(
                store_sel.xpath('//meta[@property="og:latitude"]//@content')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//meta[@property="og:longitude"]//@content')
            ).strip()

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
