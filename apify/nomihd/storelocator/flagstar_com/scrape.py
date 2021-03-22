# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "flagstar.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    done_urls_list = []
    urls_list = [
        "https://www.flagstar.com/flagstar-bank-branches-michigan.html",
        "https://www.flagstar.com/flagstar-bank-loan-centers.html",
    ]
    for search_url in urls_list:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//table[@id="branchlist-resultstable"]/tbody/tr')

        for store in stores:
            page_url = "".join(store.xpath("td[1]/a/@href"))
            location_type = "".join(store.xpath("td[5]/strong/text()")).strip()
            locator_domain = website
            location_name = "".join(store.xpath("@data-name")).strip()

            street_address = "".join(store.xpath("@data-address1")).strip()
            if len("".join(store.xpath("@data-address2")).strip()) > 0:
                street_address = (
                    street_address
                    + ", "
                    + "".join(store.xpath("@data-address2")).strip()
                )

            city = "".join(store.xpath("@data-city")).strip()
            state = "".join(store.xpath("@data-state")).strip()
            zip = "".join(store.xpath("@data-zip")).strip()
            country_code = "US"
            phone = "".join(store.xpath("@data-bankingphone")).strip()
            if len(phone) <= 0:
                phone = "".join(store.xpath("@data-loanphone")).strip()
            store_number = "".join(store.xpath("@data-branchnum")).strip()
            latitude = "".join(store.xpath("@data-lattitude")).strip()
            longitude = "".join(store.xpath("@data-longitude")).strip()
            hours_of_operation = "<MISSING>"
            if page_url in done_urls_list:
                continue
            else:
                done_urls_list.append(page_url)

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        '//div[@id="hours_branch"]//div[@itemprop="openingHours"]/text()'
                    )
                )
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", ":")
                .strip()
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
