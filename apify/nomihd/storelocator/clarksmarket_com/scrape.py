# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgselenium import SgChrome
import time

website = "clarksmarket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://clarksmarket.com/all"
    with SgChrome() as driver:
        driver.get(search_url)
        time.sleep(30)
        stores_sel = lxml.html.fromstring(driver.page_source)

        stores = stores_sel.xpath('//div[@id="allStoreContain"]/div[@class="span3"]')

        for store in stores:
            page_url = (
                "https://clarksmarket.com"
                + "".join(
                    store.xpath('p[@class="storeInfoBtnContain"]/a/@href')
                ).strip()
            )
            locator_domain = website
            location_name = "".join(store.xpath("h3/text()")).strip()

            street_address = "".join(store.xpath("p[1]/text()[1]")).strip()
            city = "".join(store.xpath('p[1]/span[@id="storeCity"]/text()')).strip()
            state = "".join(store.xpath('p[1]/span[@id="storeState"]/text()')).strip()
            zip = "".join(store.xpath("p[1]/text()[3]")).strip()
            country_code = "US"

            phone = store.xpath('p/a[contains(@href,"tel:")]/text()')
            if len(phone) > 0:
                phone = phone[0]
            else:
                phone = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(store.xpath("p[position()>1 and position()<=3]//text()"))
                .strip()
                .replace(": ;", ": ")
                .strip()
            )

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            store_number = "<MISSING>"
            try:
                store_number = (
                    store_req.text.split("var theStoreID = ")[1]
                    .strip()
                    .split(";")[0]
                    .strip()
                )
            except:
                pass

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()

            if len(map_link) > 0:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
