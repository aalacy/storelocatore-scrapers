# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "roths.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://roths.com/contact.php"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="contact-store-div"]')

    coord_list = stores_req.text.split("position: new google.maps.LatLng(")
    for index in range(0, len(stores)):
        page_url = search_url
        locator_domain = website
        location_name = "".join(
            stores[index].xpath('span[@class="contact-store-name"]/text()')
        ).strip()

        address = stores[index].xpath("a[1]/text()")
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        phone = "".join(
            stores[index].xpath('span[@class="contact-store-phone"]/a/text()')
        ).strip()
        hours_of_operation = "<MISSING>"
        street_address = ", ".join(add_list[:-1]).strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        latitude = coord_list[index + 1].split(",")[0].strip()
        longitude = coord_list[index + 1].split(",")[1].strip().split(")")[0].strip()

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
