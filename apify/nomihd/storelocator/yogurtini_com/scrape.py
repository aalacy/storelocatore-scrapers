# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "yogurtini.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.yogurtini.com/find-a-location"
    while True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath("//table/tbody/tr")
        for store in stores:
            page_url = search_url
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "Yogurtini"

            street_address = ", ".join(
                store.xpath(
                    'td//div[@class="adr"]/div[@class="street-address"]/span/text()'
                )
            )
            city = "".join(
                store.xpath(
                    'td//div[@class="adr"]/span[@itemprop="addressLocality"]/text()'
                )
            )
            state = "".join(
                store.xpath(
                    'td//div[@class="adr"]/span[@itemprop="addressRegion"]/text()'
                )
            )
            zip = "".join(
                store.xpath('td//div[@class="adr"]/span[@itemprop="postalCode"]/text()')
            )
            country_code = ""
            if us.states.lookup(state):
                country_code = "US"

            phone = "".join(store.xpath('td/a[contains(@href,"tel:")]/text()')).strip()

            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            latitude = "".join(store.xpath("td/div/@data-lat")).strip()
            longitude = "".join(store.xpath("td/div/@data-long")).strip()

            if country_code == "US":
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

        next_page = stores_sel.xpath('//li[@class="next"]/a/@href')
        if len(next_page) > 0:
            search_url = "https://www.yogurtini.com" + next_page[0].strip()
        else:
            break


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
