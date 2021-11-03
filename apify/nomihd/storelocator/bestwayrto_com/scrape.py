# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import httpx

website = "bestwayrto.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.bestwayrto.com",
    "cache-control": "max-age=0",
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
    "referer": "https://www.bestwayrto.com/find-a-store/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bestwayrto.com/find-a-store/"
    timeout = httpx.Timeout(120.0, connect=120.0)
    with SgRequests(
        dont_retry_status_codes=([404]),
        verify_ssl=False,
        proxy_country="us",
        timeout_config=timeout,
    ) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[contains(@class,"box-location flex justify-between")]'
        )

        for store in stores:

            latitude = "".join(store.xpath("@data-lat")).strip()
            longitude = "".join(store.xpath("@data-lng")).strip()
            page_url = search_url

            locator_domain = website
            store_info = store.xpath("div[1]/p/text()")
            location_name = "".join(store.xpath("div[1]/h3/text()")).strip()
            street_address = ", ".join(store_info[:-2]).strip()
            city = store_info[-2].strip().split(",")[0].strip()
            state_zip = store_info[-2].strip().split(",")[-1].strip()
            state = state_zip.split(" ")[0].strip()
            zip = state_zip.split(" ")[-1].strip()

            country_code = "US"

            store_number = "".join(store.xpath("@data-id")).strip()
            phone = "".join(store_info[-1]).strip()

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
