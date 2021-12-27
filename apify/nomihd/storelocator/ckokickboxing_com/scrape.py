# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ckokickboxing.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_url = "https://www.ckokickboxing.com/find-a-location/"
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//ul[@class="subsites"]/li[contains(@id,"maplocationsectionbottom-marker-")]'
        )
        for store in stores:
            page_url = "".join(store.xpath("a/@href")).strip()
            locator_domain = website
            location_name = "".join(
                store.xpath('span[@class="h4 nomargin"]/text()')
            ).strip()
            if len(location_name) <= 0:
                continue

            street_address = "".join(
                store.xpath('.//span[@itemprop="streetAddress"]/text()')
            ).strip()
            city = "".join(
                store.xpath('.//span[@itemprop="addressLocality"]/text()')
            ).strip()
            state = "".join(
                store.xpath('.//span[@itemprop="addressRegion"]/text()')
            ).strip()
            zip = "".join(store.xpath('.//span[@itemprop="postalCode"]/text()')).strip()

            country_code = "CA"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store.xpath('.//span[@itemprop="telephone"]/text()')
            ).strip()

            latitude = "".join(store.xpath("@data-lat")).strip()
            longitude = "".join(store.xpath("@data-lon")).strip()

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_type = "".join(
                store_sel.xpath(
                    '//h3[@class="h2 main-title"]/span[@class="h6 block"]/text()'
                )
            ).strip()

            hours_of_operation = ";".join(
                store_sel.xpath('//ul[@class="schedule-list"]/li/text()')
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
