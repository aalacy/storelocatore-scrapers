# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "timhortons.co.th"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.ihopmexico.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://timhortons.co.th/wp-sitemap-posts-stores-1.xml"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        stores = search_res.text.split("<loc>")
        for index in range(1, len(stores)):
            page_url = "".join(stores[index].split("</loc>")[0]).strip()
            log.info(page_url)

            page_res = session.get(page_url, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website
            location_name = "".join(page_sel.xpath("//title/text()")).strip()

            raw_address = page_sel.xpath(
                '//div[@class="store_locator_single_address"]/text()'
            )
            street_address = raw_address[-2]
            city = raw_address[-1].strip().split(",")[1].strip()
            state = raw_address[-1].strip().split(",")[-2].strip()
            zip = raw_address[-1].strip().split(",")[0].strip()

            country_code = "TH"

            store_number = "<MISSING>"

            phone = "".join(
                page_sel.xpath(
                    '//div[@class="store_locator_single_contact"]/a[contains(@href,"tel:")]/text()'
                )
            ).strip()
            hours_of_operation = "; ".join(
                page_sel.xpath(
                    '//div[@class="store_locator_single_opening_hours"]/text()'
                )
            ).strip()
            location_type = "<MISSING>"

            latitude = "".join(
                page_sel.xpath('//div[@id="store_locator_single_map"]/@data-lat')
            ).strip()
            longitude = "".join(
                page_sel.xpath('//div[@id="store_locator_single_map"]/@data-lng')
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
