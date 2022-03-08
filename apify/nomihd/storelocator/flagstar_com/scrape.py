# -*- coding: utf-8 -*-
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "flagstar.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.flagstar.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    # Your scraper here
    done_urls_list = []
    urls_list = [
        "https://www.flagstar.com/flagstar-bank-branches-michigan.html",
        "https://www.flagstar.com/flagstar-bank-loan-centers.html",
    ]
    with SgChrome(user_agent=user_agent) as driver:
        for search_url in urls_list:
            driver.get(search_url)
            time.sleep(10)
            stores_sel = lxml.html.fromstring(driver.page_source)
            stores = stores_sel.xpath('//table[@id="branchlist-resultstable"]/tbody/tr')

            for store in stores:
                page_url = "".join(store.xpath("td[1]//a/@href"))
                location_type = ", ".join(store.xpath("td[5]/span/span/text()")).strip()
                locator_domain = website
                location_name = "".join(store.xpath("@data-name")).strip()

                street_address = "".join(store.xpath("@data-address1")).strip()
                if len("".join(store.xpath("@data-address2")).strip()) > 0:
                    street_address = (
                        street_address
                        + ", "
                        + "".join(store.xpath("@data-address2")).strip()
                    )
                if street_address == "-":
                    street_address = "<MISSING>"
                city = "".join(store.xpath("@data-city")).strip()
                state = "".join(store.xpath("@data-state")).strip()
                zip = "".join(store.xpath("@data-zip")).strip()
                country_code = "US"
                phone = store.xpath('td[5]//a[contains(@href,"tel:")]/text()')
                if len(phone) > 0:
                    phone = phone[0]
                else:
                    phone = ""

                if len(phone) <= 0:
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
                driver.get(page_url)
                store_sel = lxml.html.fromstring(driver.page_source)
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
