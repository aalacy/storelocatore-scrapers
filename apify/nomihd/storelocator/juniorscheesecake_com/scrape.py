# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "juniorscheesecake.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.juniorscheesecake.com/blog/restaurants/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//div[@class="dropdown" and ./a[text()="Restaurants"]]//li/a/@href'
    )

    for store in stores_list:

        page_url = store
        if "/blog/restaurants/catering" in page_url:
            continue
        locator_domain = website
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(
            page_sel.xpath('//div[@class="restaurant-name"]/a/text()')
        ).strip()

        address_info = list(
            filter(
                str,
                page_sel.xpath(
                    '//div[./h4="ADDRESS"]/div[not( contains(.//text(),"-" ))]//text()'
                ),
            )
        )

        address_info = " ".join(address_info).replace("  ", " ").strip()

        raw_address = address_info

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            page_sel.xpath(
                '//div[./h4="ADDRESS"]/div[ contains(.//text(),"-" ) ]//text()'
            )
        ).strip()

        hours_info = "; ".join(
            list(filter(str, page_sel.xpath('//div[./h4="HOURS"]/div[1]//text()')))
        )
        try:
            hours_info = (
                hours_info.split("Indoor Dining:")[1].strip().split("-Stay")[0].strip()
            )
        except:
            pass

        try:
            hours_info = hours_info.split("; Outlet:")[0].strip()
        except:
            pass

        if "Temporarily Closed" in hours_info:
            location_type = "Temporarily Closed"
            hours_of_operation = "<MISSING>"
        else:
            location_type = "<MISSING>"
            hours_of_operation = hours_info

        lat_lng_href = "".join(
            page_sel.xpath('//div[@class="restaurant-name"]/a/@href')
        )

        if "z/data" in lat_lng_href:
            lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
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
