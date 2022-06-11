# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "burrislogistics.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.burrislogistics.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.burrislogistics.com/location/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="drybn-location"]')
        for store in stores:
            locator_domain = website
            page_url = "".join(
                store.xpath('.//div[@class="drybn-button--alt"]/a/@href')
            ).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = "".join(
                store_sel.xpath('//div[@class="burris-bar-title__content"]/h1/text()')
            ).strip()

            raw_address = (
                "\n".join(
                    store_sel.xpath(
                        '//div[@class="drybn-section__content "][.//h2[contains(text(),"Address")]]/p/text()'
                    )
                )
                .strip()
                .split("Phone")[0]
                .strip()
                .split("\n")
            )
            street_address = raw_address[0].strip()
            if street_address and (
                street_address[-1] == "," or street_address[-1] == "."
            ):
                street_address = "".join(street_address[:-1]).strip()
            city = raw_address[-1].strip().split(",")[0].strip()
            state = raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"
            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="drybn-section__content "][.//h2[contains(text(),"Address")]]//a[contains(@href,"tel:")]/text()'
                )
            ).strip()
            if len(phone) <= 0:
                sections = store_sel.xpath(
                    '//div[@class="drybn-section__content "][.//h2[contains(text(),"Address")]]/p/text()'
                )
                for sec in sections:
                    if "Phone" in sec:
                        phone = "".join(sec).strip().replace("Phone:", "").strip()
                        break

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            latitude = "".join(store.xpath("@data-latitude")).strip()
            longitude = "".join(store.xpath("@data-longitude")).strip()

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
