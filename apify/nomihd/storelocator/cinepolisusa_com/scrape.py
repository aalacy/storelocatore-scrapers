# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cinepolisusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.cinepolisusa.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.cinepolisusa.com/our-locations"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//a[contains(text(),"More details")]/@href')
        for store_url in stores:
            page_url = "https://www.cinepolisusa.com" + store_url
            locator_domain = website
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            raw_address = store_sel.xpath(
                '//div[./h2[contains(text(),"How to find us")]]/div/text()'
            )
            location_name = store_sel.xpath("//div/h1/text()")
            if len(location_name) > 0:
                location_name = location_name[0]

            street_address = raw_address[0].strip()
            city = raw_address[-1].strip().split(",")[0].strip()
            state = raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"
            store_number = "<MISSING>"
            phone = store_sel.xpath(
                '//div/a[contains(@href,"tel:")]/span/span[2]/text()'
            )
            if len(phone) > 0:
                phone = phone[0]
            else:
                phone = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

            map_link = "".join(
                store_sel.xpath('//a[./span[contains(text(),"Get directions")]]/@href')
            ).strip()
            latitude = map_link.split("/")[-1].strip().split(",")[0].strip()
            longitude = map_link.split("/")[-1].strip().split(",")[-1].strip()

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
