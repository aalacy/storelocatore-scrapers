# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "ffc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://ffc.com/club-locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//div[contains(@class,"club-location")]//a[contains(@aria-label,"Club Details")]/@href'
    )

    for store in store_list:

        page_url = store
        locator_domain = website
        log.info(store)
        page_res = session.get(store, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(
            page_sel.xpath('//h1[@id="main-content"]/text()')
        ).strip()

        address_info = list(
            filter(
                str,
                page_sel.xpath('//a[contains(@class,"club-address ")]//text()'),
            )
        )

        street_address = " ".join(address_info[0:-1]).strip()

        city = address_info[-1].split(",")[0].strip()

        state = address_info[-1].split(",")[1].strip().split(" ")[0].strip()
        zip = address_info[-1].split(",")[1].strip().split(" ")[1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            page_sel.xpath('//a[contains(@class,"club-phone ")]//text()')
        ).strip()

        location_type = "<MISSING>"

        hours_info = page_sel.xpath('//table[contains(@role,"presentation")]//tr')

        hour_list = []
        for tr in hours_info:
            hours = list(filter(str, tr.xpath(".//text()")))
            hours = list(filter(str, [x.strip() for x in hours]))

            hour_list.append(f"{hours[0]}: {hours[1]}")

        hours_of_operation = "; ".join(hour_list)

        lat_lng_href = "".join(
            search_sel.xpath(
                f'//div[contains(@class,"club-location") and .//text()="{location_name}"]/a[contains(@class,"club-address")]/@href'
            )
        )

        if "z/data" in lat_lng_href:
            lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
        elif "ll=" in lat_lng_href:
            lat_lng = lat_lng_href.split("ll=")[1].split("&")[0]
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[1]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        raw_address = "<MISSING>"
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
