# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "glamoursecretsbeautybar.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://glamoursecretsbeautybar.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath("//main//a/@href")  # Get all locations links

    for store in stores_list:
        page_url = store
        locator_domain = website
        if "https://glamoursecretsbeautybar.com/" in store:

            log.info(store)
            page_res = session.get(store, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)

            location_name = (
                " ".join(
                    list(
                        filter(
                            str,
                            page_sel.xpath(
                                '//*[@data-elementor-setting-key="heading_title" ]//text()'
                            ),
                        )
                    )
                )
                .replace("\n", " ")
                .replace("  ", " ")
                .replace("Welcome to", "")
                .strip()
            )
            details_info = list(
                filter(
                    str,
                    page_sel.xpath(
                        '//*[@data-elementor-setting-key="heading_description"]//text()'
                    ),
                )
            )

            details_info = (
                " ".join(details_info).replace("\n", " ").replace("  ", " ").strip()
            )

            raw_address = (
                details_info.split("phone:")[0]
                .split("working hours:")[0]
                .replace("address:", "")
                .strip()
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "CA"
            store_number = "<MISSING>"

            phone = details_info.split("phone:")[1].strip()

            location_type = "<MISSING>"

            hours_of_operation = (
                details_info.split("phone:")[0].split("working hours:")[1].strip()
            )
            map_link = "".join(
                page_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if len(map_link) > 0:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        elif "https://info.tradesecrets.ca/" in store:
            log.info(store)
            page_res = session.get(store, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)

            location_name = (
                "".join(
                    page_sel.xpath('//div[@class="fusion-text fusion-text-1"]//text()')
                )
                .strip()
                .replace("Welcome to", "")
                .strip()
            )

            address = "".join(
                page_sel.xpath(
                    '//div[@class="fusion-text fusion-text-2"]/h4[1]//text()'
                )
            ).strip()
            phone = "".join(
                page_sel.xpath(
                    '//div[@class="fusion-text fusion-text-2"]//h4[2]//text()'
                )
            ).strip()

            if len(phone) <= 0:
                address = "".join(
                    page_sel.xpath(
                        '//div[@class="fusion-text fusion-text-2"]/h4[1]//text()'
                    )
                ).strip()
                if "|" in address:
                    phone = address.split("|")[-1].strip()
                    address = address.split("|")[0].strip()

            if "or" in phone:
                phone = phone.split("or")[0].strip()

            if len(phone) <= 0:
                phone = "".join(
                    page_sel.xpath(
                        '//div[@class="fusion-text fusion-text-2"]/div/div/h4//text()'
                    )
                ).strip()
            raw_address = address
            formatted_addr = parser.parse_address_intl(address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            if "75 Centennial Parkway North On" == street_address:
                street_address = "75 Centennial Parkway North"
                state = "ON"

            country_code = "CA"

            if zip is None:
                try:
                    address = (
                        page_res.text.split('addresses: [{"address":"')[1]
                        .strip()
                        .split('",')[0]
                        .strip()
                    )
                    formatted_addr = parser.parse_address_intl(address)
                    zip = formatted_addr.postcode
                except:
                    pass

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(
                    page_sel.xpath(
                        '//div[@class="fusion-text fusion-text-3"]/h4/text()'
                    )
                )
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            if "We are OPEN." in hours_of_operation:
                hours_of_operation = (
                    "; ".join(
                        page_sel.xpath(
                            '//div[@class="fusion-text fusion-text-3"]/p/strong/text()'
                        )
                    )
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                    .replace("Operating Hours", "")
                    .strip()
                )
            latitude = "<MISSING>"
            try:
                latitude = (
                    page_res.text.split('"latitude":"')[1]
                    .strip()
                    .split('",')[0]
                    .strip()
                )
            except:
                pass
            longitude = "<MISSING>"
            try:
                longitude = (
                    page_res.text.split('"longitude":"')[1]
                    .strip()
                    .split('"')[0]
                    .strip()
                )
            except:
                pass
        else:
            continue

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
