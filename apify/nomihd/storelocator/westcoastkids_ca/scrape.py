# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "westcoastkids.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.westcoastkids.ca",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.westcoastkids.ca/contact/#"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="location-item-wrapper js-location"]')

        for store in stores:

            page_url = "".join(
                store.xpath('.//a[./span[contains(text(),"Store Information")]]/@href')
            ).strip()
            locator_domain = website

            location_name = "".join(
                store.xpath(
                    ".//div[@class='location-section location-contact-header']//text()"
                )
            ).strip()

            street_address = "".join(
                store.xpath(
                    './/ul[@class="location-contact-list"]/li[@class="icon icon-map-marker-1"]/div[@class="top"]/text()'
                )
            ).strip()

            city_state_zip = (
                "".join(
                    store.xpath(
                        './/ul[@class="location-contact-list"]/li[@class="icon icon-map-marker-1"]/div[@class="bottom"]/text()'
                    )
                )
                .strip()
                .split(" ")
            )

            city = " ".join(city_state_zip[:-3]).strip()
            state = "".join(city_state_zip[-3]).strip()
            zip = " ".join(city_state_zip[-2:]).strip()

            country_code = "CA"

            store_number = (
                "".join(
                    store.xpath(
                        ".//div[@class='location-section location-contact-header']/@id"
                    )
                )
                .strip()
                .split("-")[-1]
                .strip()
            )

            phone = "".join(
                store.xpath(
                    './/ul[@class="location-contact-list"]/li[@class="icon icon-phone"]//text()'
                )
            ).strip()

            location_type = "<MISSING>"

            hours = store.xpath('.//ul[@class="hours-list"]/li')
            hours_list = []
            for hour in hours:
                hour_val = "".join(hour.xpath("text()")).strip()
                if (
                    "DOORS OPEN:" in hour_val
                    or "CURB SIDE PICK-UP AVAILABLE" in hour_val
                ):
                    continue
                hours_list.append(hour_val)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if len(page_url) > 0:
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                store_json = json.loads(
                    "".join(store_sel.xpath('//div[@id="map"]/@data-mage-init')).strip()
                )["storeLocation"]
                latitude = store_json["latitude"]
                longitude = store_json["longitude"]
            else:
                page_url = "https://www.westcoastkids.ca/contact/#"

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
