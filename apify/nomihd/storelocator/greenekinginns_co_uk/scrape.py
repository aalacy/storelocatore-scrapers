# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "greenekinginns.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.greenekinginns.co.uk/hotels/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.greenekinginns.co.uk/hotels/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        while True:
            stores_req = session.get(
                search_url,
                headers=headers,
            )
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//div[contains(@id,"hotel-id--")]')
            for store in stores:
                page_url = (
                    "https://www.greenekinginns.co.uk"
                    + "".join(
                        store.xpath('.//h2[@class="content-block__title h6"]/a/@href')
                    ).strip()
                )
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                locator_domain = website
                location_name = "".join(
                    store_sel.xpath('//h1[@class="content-block__title h1"]/text()')
                ).strip()
                raw_address = (
                    "".join(
                        store.xpath('.//p[@class="content-block__map-address"]/text()')
                    )
                    .strip()
                    .split(",")
                )
                street_address = ", ".join(raw_address[:-3]).strip()
                city = raw_address[-3]
                state = raw_address[-2]
                zip = "".join(
                    store.xpath('.//p[@class="content-block__map-postcode"]/text()')
                ).strip()

                country_code = "GB"
                phone = (
                    "".join(
                        store_sel.xpath('//*[contains(text(),"Call Direct:")]/text()')
                    )
                    .strip()
                    .replace("Call Direct:", "")
                    .strip()
                    .split("|")[0]
                    .strip()
                )

                store_number = (
                    "".join(store.xpath("@id"))
                    .strip()
                    .replace("hotel-id--", "")
                    .strip()
                )
                location_type = store.xpath('.//svg[@class="content-block__logo"]')
                if len(location_type) > 0:
                    location_type = "OldEnglish"
                else:
                    location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"
                checkInTime = "".join(
                    store_sel.xpath(
                        '//ul[@class="hotel-info__details-list"]/li[./span[contains(text(),"Check in from")]]/span[2]/text()'
                    )
                ).strip()
                checkOutTime = "".join(
                    store_sel.xpath(
                        '//ul[@class="hotel-info__details-list"]/li[./span[contains(text(),"Check out by")]]/span[2]/text()'
                    )
                ).strip()
                if len(checkInTime) > 0 and len(checkOutTime) > 0:
                    hours_of_operation = checkInTime + " - " + checkOutTime

                latitude = "".join(
                    store_sel.xpath('//div[@id="google-static-map"]/@data-lat')
                ).strip()
                longitude = "".join(
                    store_sel.xpath('//div[@id="google-static-map"]/@data-lng')
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

            next_page = stores_sel.xpath('//li[@class="next"]/a/@href')
            if len(next_page) > 0:
                search_url = "https://www.greenekinginns.co.uk/hotels/" + next_page[0]
                log.info(search_url)
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
