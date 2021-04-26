# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "biscuitsandbath.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.biscuitsandbath.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="wp-block-columns -narrow"]/div[@class="wp-block-column"]'
    )
    for store in stores:
        page_url = "".join(
            store.xpath(".//p/span/a[contains(@href,'/locations/')]/@href")
        ).strip()
        if "biscuitsandbath" not in page_url:
            page_url = "https://www.biscuitsandbath.com" + page_url

        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(store.xpath("div[1]/div[2]/span[1]//text()")).strip()
        if len(location_name) <= 0:
            continue
        address = "".join(store.xpath("div[1]/div[2]/p[1]/a[1]/text()")).strip()
        street_address = (
            address.split(",")[0]
            .strip()
            .replace("New York", "")
            .replace(" NY", "")
            .strip()
        )
        city = "New York"
        state = address.split(",")[1].strip().split(" ")[0].strip()
        zip = address.split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = "".join(
            store.xpath('div[1]/div[2]/p[1]/a[@data-type="tel"]/text()')
        ).strip()

        temp_days = store.xpath("div[1]/div[2]/p[1]/strong/span/text()")
        days_list = []
        for day in temp_days:
            if len("".join(day).strip()) > 0:
                days_list.append("".join(day).strip())

        temp_time = store.xpath("div[1]/div[2]/p[1]/text()")
        time_list = []
        for time in temp_time:
            if len("".join(time).strip()) > 0:
                time_list.append("".join(time).strip())

        hours_list = []
        for index in range(0, len(days_list)):
            hours_list.append(days_list[index] + time_list[index])

        hours_of_operation = (
            "".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", " ")
            .strip()
        )
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
