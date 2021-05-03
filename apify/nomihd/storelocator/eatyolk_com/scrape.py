# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "eatyolk.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.eatyolk.com/contact-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="mk-accordion-single"]')

    for store in stores:
        page_url = search_url

        locator_domain = website
        location_name = "".join(store.xpath("div[1]/span/text()")).strip()
        add_list = store.xpath("div[2]//div[contains(@id,'text-block-')]/p[1]/text()")

        street_address = add_list[0].strip()
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()

        city = add_list[1].strip().split(",")[0].strip()
        state = add_list[1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].strip().split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = add_list[-1].strip().replace("Phone:", "").strip()

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = ""
        if state == "IL":
            hours_of_operation = "Daily: 7am – 2:30pm"
        elif state == "IN":
            hours_of_operation = "Daily: 7:30am – 2pm"
        elif state == "TX" or state == "FL":
            hours_of_operation = "Monday – Friday: 7am – 2:30pm; Saturday, Sunday, and Major Holidays: 7am – 3pm"

        if location_name == "TEST KITCHEN (CHICAGO)":
            hours_of_operation = "Wednesday – Sunday: 7am – 2:30pm"

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
