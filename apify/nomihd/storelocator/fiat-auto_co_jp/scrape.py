# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "fiat-auto.co.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.fiat-auto.co.jp",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fiat-auto.co.jp/dealer/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(search_res.text)
        stores = stores_sel.xpath(
            '//li[contains(@class,"cat_dealer dealer-list area_")]'
        )
        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = "".join(
                store.xpath('.//h3[@class="dealer-title"]/text()')
            ).strip()

            raw_address = (
                "".join(store.xpath('.//p[@class="dealer-address"]//text()'))
                .strip()
                .replace("<br>", "\n")
                .strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "JP"

            phone = (
                "".join(store.xpath('.//p[contains(text(),"TEL")]/text()'))
                .strip()
                .replace("TEL : ", "")
                .strip()
            )
            store_number = "<MISSING>"
            loc_type_list = []
            lables = store.xpath('.//p[@class="dealer-label"]/img/@src')
            for lab in lables:
                loc_type_list.append(
                    lab.split("/label_")[1].strip().split(".")[0].strip()
                )

            location_type = ", ".join(loc_type_list).strip()

            hours_of_operation = "; ".join(
                store.xpath('.//p[contains(text(),"TEL")]/following-sibling::p/text()')
            ).strip()
            latitude, longitude = (
                "".join(store.xpath("@data-lat")).strip(),
                "".join(store.xpath("@data-lng")).strip(),
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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
