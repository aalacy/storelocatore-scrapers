# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "bitcoinxatm.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bitcoinxatm.com/locations/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        stores = json.loads(
            search_res.text.split("var bitcoinx_maps=")[1]
            .strip()
            .split(";</script>")[0]
            .strip()
        )["locations"]

        for store in stores:

            page_url = store["url"]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//div[@class="main__wrap"]/h1/text()')
            ).strip()

            raw_address = "".join(
                store_sel.xpath('//div[@class="atm-address"]/text()')
            ).strip()

            street_address = raw_address.split(",")[0].strip()
            city = raw_address.split(",")[1].strip()
            state = raw_address.split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address.split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//div[@class="atm-detail-item atm-phone"]/span/text()')
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="atm-detail-item atm-hours"]/span/text()')
            ).strip()
            latitude, longitude = (
                store["geolocation"]["lat"],
                store["geolocation"]["lng"],
            )

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
