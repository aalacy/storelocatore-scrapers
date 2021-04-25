# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "oliverbonacini.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.oliverbonacini.com/restaurants"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    restaurants = search_sel.xpath('//div[@class="card-content"]')

    for restaurant in restaurants:
        page_url = "".join(restaurant.xpath("./a/@href")).strip()
        locator_domain = website
        location_name = "".join(restaurant.xpath("./h4/text()")).strip()

        state = (
            "".join(restaurant.xpath("./p/text()"))
            .strip()[::-1]
            .split(",")[0]
            .strip()[::-1]
        )

        city = (
            "".join(restaurant.xpath("./p/text()"))
            .strip()[::-1]
            .split(",")[1]
            .strip()[::-1]
            .split("·")[1]
            .strip()
        )

        log.info(page_url)
        restaurant_res = session.get(page_url, headers=headers)
        restaurant_sel = lxml.html.fromstring(restaurant_res.text)

        full_address = restaurant_sel.xpath(
            '//div[./a[contains(text(),"Get Direction")]]/preceding-sibling::div/p/text()'
        )
        full_address = list(filter(lambda x: len(x) > 1, full_address))

        raw_address = " ".join(full_address)

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2
        if "At The Corner Of " in street_address:
            street_address = street_address.split("At The Corner Of ")[1].strip()

        zip = formatted_addr.postcode

        country_code = "CA"
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        phone = (
            "".join(
                restaurant_sel.xpath(
                    '//div[./a[contains(text(),"Get Direction")]]/preceding-sibling::div/p/a[1]/text()'
                )
            )
            .strip()
            .replace("Brewpub", "")
            .strip()
        )

        hours_of_operation = "<MISSING>"

        map_info = "".join(
            restaurant_sel.xpath('//div[./a[contains(text(),"Get Direction")]]/a/@href')
        ).strip()

        if "maps?ll=" in map_info:
            lat_lng = map_info.split("maps?ll=")[1].split("&")[0]
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[1]
        elif "z/data" in map_info:
            lat_lng = (
                map_info.split(",17z/data")[0].split("@")[1]
                if ",17z/data" in map_info
                else map_info.split(",14z/data")[0].split("@")[1]
            )
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[1]
        else:
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
            raw_address=", ".join(raw_address.split("\n")).strip(),
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
