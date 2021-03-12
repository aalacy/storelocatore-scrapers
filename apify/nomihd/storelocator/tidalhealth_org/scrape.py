# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "tidalhealth.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.tidalhealth.org/our-locations?cat=All&text=&page=0"
    while True:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath('//div[@class="list__link"]/a/@href')
        for store_url in stores:
            page_url = "https://www.tidalhealth.org" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@class="frame mt-lg-0"]/text()')
            ).strip()

            if "," in location_name:
                location_name = location_name.split(",")[0].strip()

            address = store_sel.xpath(
                '//div[@class="views-field views-field-field-prime-location"]/div/p/text()'
            )

            street_address = address[0].strip()
            city = address[-1].strip().split(",")[0].strip()
            state = address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = address[-1].strip().split(",")[-1].strip().split(" ")[-1].strip()
            country_code = ""
            if us.states.lookup(state):
                country_code = "US"

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="views-field views-field-field-prime-location"]/div/a[@title="Contact Us"]/text()'
                )
            ).strip()

            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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

        next_page = stores_sel.xpath('//li[@class="pager__item"]/a[@rel="next"]/@href')
        if len(next_page) > 0:
            search_url = (
                "https://www.tidalhealth.org/our-locations?" + next_page[0].strip()
            )
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
