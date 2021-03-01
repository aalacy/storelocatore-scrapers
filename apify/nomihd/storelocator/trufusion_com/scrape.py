# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "trufusion.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://trufusion.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="map__locations sr-only"]/ul/li')
    for store in stores:
        page_url = "".join(
            store.xpath('div/p/strong/a[contains(text(),"VISIT LOCATION")]/@href')
        ).strip()
        log.info(page_url)
        location_name = "".join(store.xpath("div/p[1]/span/text()")).strip()

        location_type = "<MISSING>"
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website

        address = store.xpath("div/p[2]/text()")
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city = add_list[1].strip().split(",")[0].strip()
        state = add_list[1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].strip().split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        phone = "".join(
            store.xpath('div/p/strong/a[contains(@href,"tel:")]/text()')
        ).strip()

        hours = store_sel.xpath(
            '//div[@class="section__content"]/div[@class="section__entry"]/ul/li'
        )
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("span[1]/text()")).strip()
            time = "".join(hour.xpath("span[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
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
