# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thecheesecakefactoryme.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://thecheesecakefactoryme.com"
    search_url = "https://thecheesecakefactoryme.com/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        countries = search_sel.xpath('//div[@class="row choose-country"]//a')

        for idx, country in enumerate(countries, 1):

            country_url = base + "".join(country.xpath("./@href")).replace(
                "home/", "locations"
            )
            log.info(country_url)
            country_res = session.get(country_url, headers=headers)
            country_sel = lxml.html.fromstring(country_res.text)

            stores = country_sel.xpath('//div[contains(@class,"portfolio-item")]')
            locator_domain = website

            for store in stores:

                location_name = "".join(store.xpath(".//h4//text()")).strip()

                page_url = country_url

                raw_address = "<MISSING>"
                street_address = location_name.split(",")[0].strip()
                city = location_name.split(",")[-1].strip()
                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = country_url.split("/")[-3].strip().upper()

                store_number = "<MISSING>"

                phone = (
                    list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store.xpath(
                                    './/a[contains(@href,"tel:")]//text()'
                                )
                            ],
                        )
                    )[0]
                    .strip()
                    .strip("| ")
                    .strip()
                )
                location_type = "<MISSING>"
                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/div[contains(@class,"loc-hours")]//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = (
                    "; ".join(hours)
                    .strip()
                    .replace("FRI;", "FRI:")
                    .replace("SUN;", "SUN:")
                    .replace("SAT;", "SAT:")
                    .replace("MON;", "MON:")
                    .strip()
                )

                latitude, longitude = "<MISSING>", "<MISSING>"

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
