# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "drummondbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://drummondbank.com/find-a-branch"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="sf_colsIn locations__results"]/article')
    for store in stores:
        page_url = "".join(
            store.xpath('.//a[contains(text(),"VIEW BRANCH DETAILS")]/@href')
        ).strip()

        location_name = "".join(
            store.xpath(".//span[@class='location-card__title location-title']/text()")
        ).strip()
        location_type = "".join(
            store.xpath(".//span[@class='location-card__type location-type']/text()")
        ).strip()
        locator_domain = website
        phone = "".join(
            store.xpath('.//*[@class="location-card__phone"]/text()')
        ).strip()

        add_list = store.xpath('.//span[@class="location-card__address"]/text()')

        street_address = add_list[0].strip()
        city = add_list[1].strip().split(",")[0].strip()
        state = add_list[1].strip().split(",")[1].strip()
        zipp = add_list[-1].strip()

        hours_of_operation = ""
        hours = store.xpath('.//div[@class="location-card__hours"]')
        if len(hours) > 0:
            hours_of_operation = "; ".join(
                hours[0].xpath('span[@class="location-card__hours-item"]/text()')
            ).strip()

        country_code = "US"
        store_number = "<MISSING>"

        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lng")).strip()

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
