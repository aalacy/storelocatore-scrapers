# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "homeruninnpizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.homeruninnpizza.com/restaurants/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="locations-result-title"]/a/@href')

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@class="hero-heading"]/text()')
        ).strip()

        address = store_sel.xpath('//div[@class="location-detail-address"]/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = " ".join(add_list[:-1]).strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(
            store_sel.xpath('//div[@class="location-detail-phone"]//text()')
        ).strip()
        location_type = "<MISSING>"

        hours = store_sel.xpath(
            '//div[@id="tabs-hours"]//div[@class="col col-xs-12 col-sm-10"]//text()'
        )
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                if (
                    "Carryout, Curbside, and Delivery" in "".join(hour).strip()
                    or "Carry-out, Curbside, and Delivery" in "".join(hour).strip()
                ):
                    break
                else:
                    if (
                        "General:" not in "".join(hour).strip()
                        and "Dine-In" not in "".join(hour).strip()
                        and "Dine In" not in "".join(hour).strip()
                    ):
                        hours_list.append("".join(hour).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
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
