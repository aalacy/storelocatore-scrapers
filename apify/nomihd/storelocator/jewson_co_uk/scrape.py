# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jewson.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jewson.co.uk/branch-finder"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//a[contains(text(),"More details")]/@href')

        for store_url in stores:
            page_url = "https://www.jewson.co.uk" + store_url

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@itemprop="name"]/text()')
            ).strip()

            street_address = "".join(
                "".join(store_sel.xpath('//span[@itemprop="streetAddress"]/text()'))
                .strip()
                .split("\n")
            )
            if street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            city = "".join(
                store_sel.xpath('//span[@itemprop="addressLocality"]/text()')
            ).strip()
            if city[-1] == ",":
                city = "".join(city[:-1]).strip()

            state = "<MISSING>"
            zip = "".join(
                store_sel.xpath('//span[@itemprop="postalCode"]/text()')
            ).strip()
            country_code = "GB"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//span[@itemprop="telephone"]/text()')
            ).strip()

            location_type = "<MISSING>"

            latitude = "".join(
                store_sel.xpath('//div[@id="store_google_map"]/@data-latitude')
            ).strip()
            longitude = "".join(
                store_sel.xpath('//div[@id="store_google_map"]/@data-longitude')
            ).strip()

            hours = store_sel.xpath(
                '//table[@class="table mb-0 table--no-border table--p-5"]/tr'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]/text()")).strip()
                hours_list.append("".join(day.split("\n")) + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

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
