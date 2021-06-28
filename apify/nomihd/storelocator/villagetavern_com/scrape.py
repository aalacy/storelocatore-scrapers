# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "villagetavern.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://villagetavern.com/"
    home_req = session.get(search_url, headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    sections = home_sel.xpath('//ul[@class="menu vertical"]')

    for index in range(0, len(sections)):
        if (
            "LOCATIONS"
            in "".join(sections[index].xpath('li[@class="menu-title"]/text()')).strip()
        ):
            stores = sections[index].xpath("li/a/@href")
            for store_url in stores:
                page_url = store_url
                locator_domain = website
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                location_name = "".join(
                    store_sel.xpath('//h1[@class="page-title text-center"]/text()')
                ).strip()

                address = store_sel.xpath(
                    '//div[@class="contact-info"]/p[@class="address"]/text()'
                )
                street_address = ""
                if len(address) == 3:
                    street_address = address[1]
                elif len(address) == 2:
                    street_address = address[0]

                city = address[-1].split(",")[0].strip()
                state = address[-1].split(",")[1].strip().split(" ")[0].strip()
                zip = address[-1].split(",")[1].strip().split(" ")[-1].strip()
                country_code = "US"

                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="contact-info"]/p[@class="phone"]//text()'
                    )
                ).strip()

                store_number = "<MISSING>"
                location_type = "<MISSING>"

                hours_of_operation = " ".join(
                    store_sel.xpath('//p[@class="hours"]//text()')
                ).strip()
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                latitude = (
                    store_req.text.split("latitude = ")[1].strip().split(",")[0].strip()
                )
                longitude = (
                    store_req.text.split("longitude = ")[1]
                    .strip()
                    .split(",")[0]
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

            break


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
