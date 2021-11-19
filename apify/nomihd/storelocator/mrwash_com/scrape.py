# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "mrwash.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "mrwash.com",
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
    search_url = "https://mrwash.com/locations/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//ul[@class="elementor-icon-list-items"][1]//a/@href'
        )
        for store_url in stores:
            if "facebook" in store_url:
                break
            page_url = store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = " ".join(
                store_sel.xpath(
                    '//div/h2[@class="elementor-heading-title elementor-size-large"]/text()'
                )
            ).strip()

            raw_address = "".join(
                store_sel.xpath(
                    '//li[@class="elementor-icon-list-item"][.//span/i[@class="fas fa-location-arrow"]]//span[@class="elementor-icon-list-text"]/text()'
                )
            ).strip()
            if len(raw_address) <= 0:
                raw_address = (
                    store_req.text.split("wash located at")[1]
                    .strip()
                    .split("<")[0]
                    .strip()
                )

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            if street_address == "3013 Gallows Road Fls":
                street_address = "3013 Gallows Road"
                city = "Falls Church"

            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//li[@class="elementor-icon-list-item"][./span/i[@class="fas fa-phone"]]/span[@class="elementor-icon-list-text"]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            days = store_sel.xpath(
                '//div[./div/h2[contains(text(),"Hours of operation") or contains(text(),"hours of Operation") or contains(text(),"hours of operation")]]/following-sibling::div[1]//h5/b/text()'
            )

            time = store_sel.xpath(
                '//div[./div/h2[contains(text(),"Hours of operation") or contains(text(),"hours of Operation") or contains(text(),"hours of operation")]]/following-sibling::div[1]//h5/text()'
            )
            if len(time) <= 0:
                time = store_sel.xpath(
                    '//div[./div/h2[contains(text(),"Hours of operation") or contains(text(),"hours of Operation") or contains(text(),"hours of operation")]]/following-sibling::div[1]//h5[./span/b]/span/b/text()'
                )
            hours_list = []
            for index in range(0, len(time)):
                hours_list.append(
                    "".join(days[index]).strip() + ": " + "".join(time[index]).strip()
                )

            hours_of_operation = "; ".join(hours_list).strip()
            if page_url == "https://mrwash.com/silver-spring-md/":
                hours_of_operation = (
                    " ".join(
                        store_sel.xpath(
                            '//div[./div/h2[contains(text(),"Hours of operation") or contains(text(),"hours of Operation") or contains(text(),"hours of operation")]]/following-sibling::div[1]//h5/b/text()'
                        )
                    )
                    .strip()
                    .replace(" pm", " pm;")
                    .strip()
                )

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
