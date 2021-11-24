# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "ecommunity.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    page_no = 0

    while True:
        base = "https://www.ecommunity.com"
        search_url = f"https://www.ecommunity.com/locations?page={page_no}"
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores_list = search_sel.xpath(
            '//div[contains(@class,"list-result")]//li/div/a/@href'
        )
        if not stores_list:
            break
        else:
            page_no += 1

        for store in stores_list:

            page_url = base + store
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)
            locator_domain = website

            location_name = "".join(page_sel.xpath("//div[@class]/h1/text()")).strip()

            address_info = list(
                filter(
                    str,
                    page_sel.xpath('//div[contains(@class,"address")]/p/span/text()'),
                )
            )

            if len(address_info) <= 0:
                log.info("different url format")
                continue
            street_address = address_info[0].strip()

            city = address_info[1].strip().split(" ")[0].strip(" ,")
            state = address_info[1].strip().split(" ")[1].strip()
            zip = address_info[1].strip().split(" ")[2].strip()
            country_code = "US"

            store_number = "<MISSING>"

            phone = page_sel.xpath('//div[contains(@class,"phone")]/a/text()')
            if len(phone) > 0:
                phone = "".join(phone[0]).strip()
            else:
                phone = "<MISSING>"

            location_type = "<MISSING>"

            hours_info = (
                " | ".join(
                    page_sel.xpath(
                        '//div[contains(@class,"hours-of-operation")]/p[not(@class)][1]//text()'
                    )
                )
                .replace(", ", ": ")
                .replace("noon", "noon; ")
                .replace("p.m.", "p.m.; ")
                .replace("; )", ") ")
                .replace("Phones:", "")
                .replace("\n", "")
                .replace("a week", "a week; ")
                .replace(" | ", "")
                .strip(" |;")
            )
            if (
                True
                in [
                    day in hours_info
                    for day in [
                        "Mon",
                        "Tue",
                        "Thur",
                        "Fri",
                        "Sat",
                        "Sun",
                        "Daily",
                        "Open 24/7",
                    ]
                ]
                and "closed permanently" not in hours_info
                and "TEMPORARILY CLOSED" not in hours_info
            ):
                hours_of_operation = hours_info
            else:

                if "closed permanently" in hours_info:
                    continue
                elif "TEMPORARILY CLOSED" in hours_info:
                    location_type = "Temporarily Closed"
                    hours_of_operation = "<MISSING>"
                elif "Now Open!" in hours_info or "NOW OPEN!" in hours_info:
                    hours_info = (
                        " | ".join(
                            page_sel.xpath(
                                '//div[contains(@class,"hours-of-operation")]/p[not(@class)][1]//text()'
                            )
                        )
                        .replace(", ", ": ")
                        .replace("noon", "noon; ")
                        .replace("p.m.", "p.m.; ")
                        .replace("; )", ") ")
                        .replace("Phones:", "")
                        .replace("\n", "")
                        .replace("a week", "a week; ")
                        .replace(" | ", "")
                        .strip(" |;")
                    )
                else:  # Handling outliers
                    hours_info = (
                        " ".join(
                            page_sel.xpath(
                                '//div[contains(@class,"hours-of-operation")]/p[contains(text(), "To schedule, call")]/following-sibling::p[not(@class)]//text()'
                            )
                        )
                        .replace("\n", ", ")
                        .strip()
                    )
                    hours_of_operation = hours_info

            latitude = (
                page_res.text.split('"latitude":')[1]
                .split(",")[0]
                .strip()
                .replace('"', "")
                .strip()
            )
            longitude = (
                page_res.text.split('"longitude":')[1]
                .split("}")[0]
                .strip()
                .replace('"', "")
                .strip()
            )

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
