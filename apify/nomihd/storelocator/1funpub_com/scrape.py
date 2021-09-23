# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "1funpub.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.1funpub.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.1funpub.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location-block"]')

    hours_sel = lxml.html.fromstring(
        session.get("https://www.1funpub.com/", headers=headers).text
    )

    for store in stores:
        page_url = (
            "https://www.1funpub.com"
            + "".join(
                store.xpath('.//a[./h2[@class="heading-jumbo-small locations"]]/@href')
            ).strip()
        )

        location_name = "".join(
            store.xpath('.//a/h2[@class="heading-jumbo-small locations"]/text()')
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website

        raw_address = list(
            filter(
                str,
                store.xpath('.//a/p[@class="paragraph-light locations"]/text()'),
            )
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip().split(",")[0].strip()
        state = raw_address[1].strip().split(",")[-1].strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        zip = json.loads(
            "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
        )["address"]["postalCode"]

        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(
            store.xpath(
                './/a[@class="location-phone-link" and contains(@href,"tel:")]/text()'
            )
        ).strip()

        hours = list(filter(str, hours_sel.xpath('//div[@class="hours-text"]/text()')))
        hours_of_operation = (
            "; ".join(hours)
            .strip()
            .replace("Hours of Operation:;", "")
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "")
            .strip()
        )

        if hours_of_operation:
            if hours_of_operation[-1] == ";":
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

        latlng = "".join(
            store.xpath(
                './/div[@class="location-map w-widget w-widget-map"]/@data-widget-latlng'
            )
        ).strip()
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[-1].strip()

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
