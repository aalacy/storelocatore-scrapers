# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "altonlane.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "altonlane.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://altonlane.com/pages/shopping-reimagined"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="Showroom__grid__description"]')

    for store in stores:

        page_url = search_url
        locator_domain = website

        location_name = "".join(
            store.xpath('.//h3[@class="Showroom__grid__item__title"]/text()')
        ).strip()

        address = store.xpath('.//p[@class="Showroom__grid__item__address"]/text()')
        street_address = ""
        city = ""
        state = ""
        zip = ""
        if len(address) > 1:
            street_address = "".join(address[:-2]).strip().replace("\n", "").strip()
            city = address[-2].strip().split(",")[0].strip()
            state = address[-2].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = address[-2].strip().split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = address[-1].strip()
        location_type = "<MISSING>"
        hours_of_operation = (
            "; ".join(store.xpath('.//p[@class="Showroom__grid__item__hours"]/text()'))
            .strip()
            .replace(",", ":")
            .strip()
            .replace("\n", "")
            .strip()
        )

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
