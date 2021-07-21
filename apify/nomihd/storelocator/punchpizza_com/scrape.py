# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html


website = "punchpizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://punchpizza.com"

    search_url = "https://punchpizza.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = list(set(search_sel.xpath('//ul[@id="homelocations"]/li/a/@href')))

    for store in stores_list:

        page_url = base + store
        log.info(page_url)
        page_res = session.get(page_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)
        locator_domain = website

        location_name = "".join(
            page_sel.xpath('//div[@class="wpb_wrapper"]/p[not(./a)]/text()')
        ).strip()

        address_info = page_sel.xpath(
            '//p[./a[contains(@href,"tel:")]]/preceding-sibling::p/a//text()'
        )
        address_info = list(filter(str, [x.strip(" \n") for x in address_info]))

        street_address = (
            "".join(address_info[0]).replace("\n", " ").replace("  ", " ").strip()
        )

        cty_st_zip = address_info[1]
        city = " ".join(cty_st_zip.split(" ")[:-2]).strip(" ,")
        state = cty_st_zip.split(" ")[-2].strip()
        zip = cty_st_zip.split(" ")[-1].strip()
        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(page_sel.xpath('//p[./a[contains(@href,"tel:")]]/a//text()'))

        location_type = (
            "Temporarily Closed"
            if "".join(page_sel.xpath("//em/text()")) == "Temporarily Closed"
            else "<MISSING>"
        )

        hours_info = page_sel.xpath(
            '//p[./a[contains(@href,"tel:")]]/following::p[not(./a)]/text()'
        )
        hours_info = list(filter(bool, [x.strip(" \n") for x in hours_info]))

        hours_of_operation = (
            "; ".join(hours_info)
            .replace("day", "day:")
            .replace(":-", "-")
            .replace(":s", "s")
            .replace(":;", ":")
            .replace("Store Hours:", "")
            .strip()
        )

        lat_lng = page_res.text.split("var punchloc = {")[1].split("};")[0]

        latitude = lat_lng.split(",")[0].replace("lat:", "").strip()
        longitude = lat_lng.split(",")[1].replace("lng:", "").strip()

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
