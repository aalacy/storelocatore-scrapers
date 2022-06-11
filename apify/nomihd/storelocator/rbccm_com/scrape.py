# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "rbccm.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.rbccm.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.rbccm.com/en/offices/our-offices.page"
    with SgRequests() as session:
        countries_req = session.get(search_url, headers=headers)
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath(
            '//div[@id="all"]//a[@class="img-stretch office-country-tile tile"]'
        )
        for country in countries:
            country_code = "".join(
                country.xpath('.//span[@class="office-country-title"]/text()')
            ).strip()
            country_url = (
                "https://www.rbccm.com" + "".join(country.xpath("@href")).strip()
            )
            log.info(country_url)
            stores_req = session.get(country_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//div[./div[@class="office-card tile"]]')
            for store in stores:
                page_url = country_url
                locator_domain = website
                location_name = "".join(
                    store.xpath("div[@class='office-card tile']/h3/text()")
                ).strip()
                raw_address = (
                    ", ".join(store.xpath('.//p[@class="office--address"]/text()'))
                    .strip()
                    .replace(" , ", ", ")
                    .strip()
                )

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address:
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                else:
                    if formatted_addr.street_address_2:
                        street_address = formatted_addr.street_address_2

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                store_number = "<MISSING>"
                phone = store.xpath(".//p[@class='offices--phone-number']/text()")
                if len(phone) > 0:
                    phone = phone[0].replace("Main:", "").strip()
                else:
                    phone = "<MISSING>"

                location_type = "<MISSING>"

                latitude = "<MISSING>"
                longitude = "<MISSING>"

                hours_of_operation = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
