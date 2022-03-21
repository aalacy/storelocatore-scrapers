# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "benny-co.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.benny-co.com/trouver-une-rotisserie/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//article[@class="w2dc-listing-location"]')
    for store in stores:
        page_url = "".join(
            store.xpath('div/a[@class="w2dc-btn w2dc-btn-primary"]/@href')
        ).strip()
        log.info(page_url)
        locator_domain = website
        location_name = "".join(
            store.xpath(
                './/div[@class="w2dc-map-listing-content-wrap"]/header/h2/text()'
            )
        ).strip()

        street_and_city = "".join(
            store.xpath('.//span[@itemprop="streetAddress"]/text()')
        ).strip()
        street_address = ", ".join(street_and_city.split(",")[:-1]).strip()
        city = "".join(street_and_city.split(",")[-1]).strip()
        state = "".join(
            store.xpath('.//span[@itemprop="addressLocality"]/text()')
        ).strip()
        zip = "".join(store.xpath('.//span[@itemprop="postalCode"]/text()')).strip()

        country_code = "CA"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()')).strip()
        hours_of_operation = ""
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        if (
            "OUVERTURE"
            in "".join(
                store_sel.xpath('//div[@class="noteHeuresOuverture"]/p/text()')
            ).strip()
        ):
            log.info("skipped!!!!")
            continue
        hours = store_sel.xpath('//div[@class="heuresOuverture"]')
        hours_list = []
        if len(hours) > 0:
            hours = hours[0].xpath("span")
            for hour in hours:
                day = "".join(hour.xpath('span[@class="jour"]/text()')).strip()
                time = "".join(hour.xpath('span[@class="heures"]/text()')).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        map_link = "".join(
            store.xpath('.//a[contains(@href,"maps/dir/")]/@href')
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
