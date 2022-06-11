# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "leekunited.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.leekunited.co.uk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://www.leekunited.co.uk/branches/"
        stores_req = session.get(
            search_url,
            headers=headers,
        )
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="pod"]/a/@href')
        for store_url in stores:
            page_url = "https://www.leekunited.co.uk" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//*[@id="section-"]/div/div/div/h2[1]/text()')
            ).strip()
            raw_address = "".join(
                store_sel.xpath(
                    '//div[@class="pod"]/div[./h3[text()="Contact the branch"]]/p[1]//text()'
                )
            ).strip()

            raw_address = raw_address.split(",")
            street_address = ", ".join(raw_address[:-3]).strip()
            city = raw_address[-3]

            state = "".join(raw_address[-2]).strip()
            zip = "".join(raw_address[-1]).strip()
            country_code = "GB"
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="pod"]/div[./h3[text()="Contact the branch"]]/p[./span/strong[text()="Tel:"]]/span/text()'
                )
            ).strip()

            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        '//div[@class="pod"]/div[./h3[text()="Opening times"]]/p[1]/text()'
                    )
                )
                .strip()
                .replace("\r\n", "")
                .strip()
                .replace("\n", "")
                .strip()
                .replace("; ;", "")
                .strip()
            )
            if hours_of_operation and hours_of_operation[-1] == ";":
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"
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
