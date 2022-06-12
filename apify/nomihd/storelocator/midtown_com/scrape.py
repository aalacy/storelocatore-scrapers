# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "midtown.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.midtown.com"

    search_url = "https://www.midtown.com/our-clubs"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = list(
        set(
            search_sel.xpath(
                '//li[.//a[text()="Our Clubs"]]//li[contains(@class, "leaf")]/a/@href'
            )
        )
    )

    for store in stores_list:

        page_url = base + store
        locator_domain = website
        log.info(page_url)
        page_res = session.get(page_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(page_sel.xpath("//title/text()")).strip()

        address_info = list(
            filter(
                str,
                page_sel.xpath(
                    '//div[contains(@class,"details")]//node()[@class="address-1" or  @class="address-2" ]//text()'
                ),
            )
        )
        raw_address = " ".join(address_info)

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "CA" if " " in zip else "US"

        store_number = "".join(page_sel.xpath("//section[@data-bid]/@data-bid"))

        phone = "".join(
            list(
                filter(
                    lambda x: True if "-" in x else False,
                    page_sel.xpath(
                        '//*[contains(text(),"MANAGER") or contains(text(),"anager")]/following-sibling::div[contains(.//text(),"-") ]//text()'
                    ),
                )
            )
        ).strip()

        location_type = "<MISSING>"
        hour_xpath = '//div[ (./preceding-sibling::h3[contains(text(),"HOUR") or contains(text(),"hour") or contains(text(),"Hour")]) and (./following-sibling::h3[contains(text(),"MANAGER") or contains(text(),"anager")])]//text()'
        hours_of_operation = (
            " ".join(list(filter(str, page_sel.xpath(hour_xpath))))
            .replace("\n", " ")
            .replace("  ", " ")
            .strip()
        )

        latitude = "".join(
            page_sel.xpath('//div[contains(@class,"google-map")]/@data-lat')
        )
        longitude = "".join(
            page_sel.xpath('//div[contains(@class,"google-map")]/@data-lng')
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
