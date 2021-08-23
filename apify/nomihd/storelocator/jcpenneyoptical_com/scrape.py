# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jcpenneyoptical.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.jcpenneyoptical.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jcpenneyoptical.com/stores/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="shops-list"]//div[contains(@class,"store-info ")]'
    )
    for store in stores:
        page_url = "".join(store.xpath('.//div[@class="direction"]/h4/a/@href')).strip()

        store_number = "".join(store.xpath("@id")).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@itemprop="name"]/text()')
        ).strip()
        street_address = "".join(
            store_sel.xpath(
                '//p[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//p[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//p[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//p[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
            )
        ).strip()

        country_code = "US"

        phone = "".join(
            store_sel.xpath(
                '//p[@itemprop="address"]/span[@itemprop="telephone"]//text()'
            )
        ).strip()
        location_type = "<MISSING>"
        latlng = "".join(store_sel.xpath("//a[@data-coord]/@data-coord")).strip()
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[-1].strip()

        hours = store_sel.xpath('//p[@class="hours"]/span[@itemprop="openingHours"]')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("strong/text()")).strip()
            time = "".join(hour.xpath("text()")).strip()
            hours_list.append(day + time)

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
