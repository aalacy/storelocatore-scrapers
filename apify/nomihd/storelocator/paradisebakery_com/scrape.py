# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "paradisebakery.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://paradisebakery.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    cities_list = search_sel.xpath(
        '//a[contains(@href,"locations")]/following::ul[@style="display:none"]/li/a/@href'
    )

    for city in cities_list:

        page_url = "https://www.paradisebakery.com/locations"
        locator_domain = website
        log.info(city)
        page_res = session.get(city, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        stores_list = page_sel.xpath(
            '//div[contains(@id,"Container")]//div[@data-testid="richTextElement" and ./h1[contains(@style,"font-size:23px")]/span[text()]]'
        )

        for store in stores_list:

            location_name = " ".join(
                store.xpath(
                    './h1[contains(@style,"font-size:23px")]/span[text()]/text()'
                )
            ).strip()

            raw_address = (
                " ".join(
                    list(
                        filter(
                            str,
                            store.xpath(
                                './h1[contains(@style,"font-size:16px")]//span[text()]//text()'
                            ),
                        )
                    )
                )
                .replace("\n", " ")
                .replace("  ", " ")
                .strip()
            )

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            street_address = street_address.replace("Ste", "Suite")  # Suite in address

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"

            phone = (
                "".join(
                    list(
                        filter(
                            str,
                            store.xpath(
                                './h1[contains(@style,"font-size:21px")]//span[text()]//text()'
                            ),
                        )
                    )
                )
                .replace("\n", " ")
                .replace("  ", " ")
                .strip()
            )
            location_type = "<MISSING>"

            hours_list = list(
                filter(
                    str, store.xpath('./p[contains(@style,"font-size:14px")]//text()')
                )
            )
            hours_of_operation = (
                " ".join([hour.strip() for hour in hours_list])
                .split("Takeout")[0]
                .split("Breakfast")[0]
                .replace("\n", " ")
                .replace("  ", " ")
                .strip()
                .replace("Hours :", "")
                .strip()
                .replace("Hours:", "")
                .strip()
            )
            if "Please visit" in hours_of_operation and "closed" in hours_of_operation:
                continue

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
