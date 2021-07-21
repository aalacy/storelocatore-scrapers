# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "gbankmo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.gbankmo.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.gbankmo.com/about/locations-hours.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[@class="loc"]')
    for store in stores:
        page_url = (
            "https://www.gbankmo.com"
            + "".join(store.xpath('.//a[@class="seeDetails"]/@href')).strip()
        )

        locator_domain = website

        location_name = "".join(store.xpath("@data-title")).strip()

        street_address = "".join(store.xpath("@data-address1")).strip()
        if len("".join(store.xpath("@data-address2")).strip()) > 0:
            street_address = (
                street_address + ", " + "".join(store.xpath("@data-address2")).strip()
            )
        city = "".join(store.xpath("@data-city")).strip()
        state = "".join(store.xpath("@data-state")).strip()
        zip = "".join(store.xpath("@data-zip")).strip()

        country_code = "US"

        store_number = page_url.split("?id=")[1].strip().split("&")[0].strip()

        phone = "".join(
            store.xpath(
                './/div[@class="contact"][.//span[contains(text(),"Phone")]]//span[@class="value"]/text()'
            )
        ).strip()

        hours = store.xpath('.//div[@class="lobbyHours"]/div')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath('span[@class="key"]/text()')).strip()
            time = "".join(hour.xpath('span[@class="value"]/text()')).strip()
            hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(hours_list).strip()

        location_type = "<MISSING>"
        latitude = "".join(store.xpath("@data-latitude")).strip()
        longitude = "".join(store.xpath("@data-longitude")).strip()

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
