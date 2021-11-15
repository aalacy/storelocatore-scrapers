# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import urllib.parse

website = "mexicaninncafe.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.mexicaninncafe.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.mexicaninncafe.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.mexicaninncafe.com/locations"

    with SgRequests(dont_retry_status_codes=set([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            '//div[@class="sqs-gallery"]//div[@class="margin-wrapper"]/a[not(@target)]'
        )
        for store in stores:

            page_url = (
                "https://www.mexicaninncafe.com" + "".join(store.xpath("@href")).strip()
            )
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = (
                page_url.split("/")[-1].strip().replace("-", " ").strip().upper()
            )

            raw_address = (
                "".join(store_sel.xpath('.//a[contains(text(),"Directions")]/@href'))
                .strip()
                .split("maps/place/")[1]
                .strip()
                .split("/")[0]
                .strip()
            )
            raw_address = urllib.parse.unquote(raw_address.replace("+", " ")).split(",")
            street_address = ", ".join(raw_address[:-2]).strip()
            city = raw_address[-2]
            state = raw_address[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()
            country_code = "US"
            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]/text()')
            ).strip()

            location_type = "<MISSING>"
            if "Temporarily Closed" in page_res.text:
                location_type = "Temporarily Closed"

            hours = store_sel.xpath(
                '//div[@class="sqs-block html-block sqs-block-html"]//p[strong]'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("text()")).strip()
                time = "".join(hour.xpath("strong/text()")).strip()
                if len(day) > 0:
                    hours_list.append(day + ": " + time)

            hours_of_operation = "; ".join(hours_list)
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
