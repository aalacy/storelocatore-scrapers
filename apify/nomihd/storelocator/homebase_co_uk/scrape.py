# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html


website = "homebase_co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "store.homebase.co.uk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://store.homebase.co.uk/"
    search_url = "https://store.homebase.co.uk/index.html"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(search_sel.xpath('//li[contains(@class,"list")]//a/@href'))

    for store in store_list:

        page_url = base + store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        locations = store_sel.xpath('//li[contains(@class,"list")]//h2/a/@href')

        if not locations:
            # append dummy location
            locations.append("dummy_location")

        for location in locations:
            if location != "dummy_location":
                # send new request and update the selector
                page_url = base + location  # update page_url
                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)  # update page_url

            location_name = "".join(
                store_sel.xpath('//*[contains(@id,"location-name")]//text()')
            )

            street_address = "".join(
                store_sel.xpath('//*[contains(@itemprop,"streetAddress")]/@content')
            )

            city = "".join(
                store_sel.xpath(
                    '//*[contains(@itemprop,"address")]//*[contains(@class,"city")]//text()'
                )
            )
            state = "<MISSING>"
            zip = "".join(
                store_sel.xpath(
                    '//*[contains(@itemprop,"address")]//*[contains(@class,"postalCode")]//text()'
                )
            )

            country_code = "GB"

            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath('//*[contains(@itemprop,"telephone")]//text()')
            ).strip()

            location_type = store_sel.xpath(
                '//span[@class="Core-heroPromoHeading"]/text()'
            )

            if len(location_type) > 0:
                location_type = location_type[0].strip()
                if "Click & Collect at this store" in location_type:
                    location_type = "<MISSING>"

            hours_of_operation = "; ".join(
                store_sel.xpath('//*[contains(@itemprop,"openingHours")]/@content')
            )

            latitude = "".join(
                store_sel.xpath('//*[contains(@itemprop,"latitude")]/@content')
            )
            longitude = "".join(
                store_sel.xpath('//*[contains(@itemprop,"longitude")]/@content')
            )

            raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
