# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "horizonbankne.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(dont_retry_status_codes=([404]), proxy_country="us")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.horizonbankne.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    cities_list = search_sel.xpath(
        '//li[.//p[contains(text(),"LOCATIONS")]]/ul/li/a/@href'
    )

    for city_url in cities_list:

        page_url = city_url
        locator_domain = website
        log.info(city_url)
        page_res = session.get(city_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(
            page_sel.xpath('//span[@style="color:#292929"]/text()')
        ).strip()

        street_address = (
            "".join(
                list(
                    filter(
                        str,
                        page_sel.xpath(
                            '//div[@data-testid="richTextElement"][./p/a[contains(@href,"google.com")]]/p[1]/text()'
                        ),
                    )
                )
            )
            .split("-")[-1]
            .strip()
        )

        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[-1].strip()
        zip = "<MISSING>"

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        phone = ""
        hours_of_operation = ""
        if len(street_address) > 0:

            phone = "".join(
                list(
                    filter(
                        str,
                        page_sel.xpath(
                            '//div[@data-testid="richTextElement"][./p/a[contains(@href,"google.com")]]/p/a/text()'
                        ),
                    )
                )
            ).strip()

            hours_of_operation = (
                "; ".join(
                    page_sel.xpath(
                        '//div[@data-testid="richTextElement"][./p[contains(text(),"Lobby Hours")]]/p[2]/text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )

            if "," in street_address:
                zip = (
                    street_address.split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                )
                street_address = street_address.split(",")[0].strip()

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

        else:
            stores = list(
                filter(
                    str,
                    page_sel.xpath(
                        '//div[@data-testid="richTextElement"][./p//a[contains(@href,"google.com")]]'
                    ),
                )
            )
            hours = page_sel.xpath(
                '//div[@data-testid="richTextElement"][./p//span[contains(text(),"Lobby ")]]'
            )
            for index in range(0, len(stores)):
                street_address = (
                    "-".join(stores[index].xpath("p[1]/span/span/span/text()"))
                    .strip()
                    .split("-")[-1]
                    .strip()
                )
                phone = "".join(
                    stores[index].xpath('./p//a[contains(@href,"google.com")]/text()')
                ).strip()
                hours_of_operation = (
                    "; ".join(hours[index].xpath("p[3]//text()"))
                    .strip()
                    .replace("\n", "")
                    .strip()
                )

                if "," in street_address:
                    zip = (
                        street_address.split(",")[-1]
                        .strip()
                        .split(" ")[-1]
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "")
                        .strip()
                    )
                    street_address = street_address.split(",")[0].strip()

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
