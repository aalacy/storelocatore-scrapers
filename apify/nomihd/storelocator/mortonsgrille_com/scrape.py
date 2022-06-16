# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import httpx

website = "mortonsgrille.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.mortonsgrille.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_urls_list = [
        "https://www.mortonsgrille.com/location/mortons-grille/",
        "https://www.mortonsgrille.com/locations/international.asp",
    ]
    timeout = httpx.Timeout(120.0, connect=120.0)

    with SgRequests(
        dont_retry_status_codes=([404]), timeout_config=timeout, verify_ssl=False
    ) as session:
        for search_url in search_urls_list:
            search_res = session.get(search_url, headers=headers)

            search_sel = lxml.html.fromstring(search_res.text)
            stores = search_sel.xpath(
                '//section/div[@class="row"]/div[.//a[contains(@href,"goo")]]'
            )

            locator_domain = website
            for store in stores:

                page_url = search_url
                location_name = "".join(store.xpath("h2/text()")).strip()
                country_code = "<MISSING>"

                raw_address = (
                    ", ".join(store.xpath('.//a[contains(@href,"goo")]/text()'))
                    .strip()
                    .replace("\n", "")
                    .strip()
                    .replace(",,", ",")
                    .strip()
                )
                phone = (
                    "".join(store.xpath('.//a[contains(@href,"tel:")]/text()'))
                    .strip()
                    .replace("+", "")
                    .strip()
                )
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                if location_name == "Hours & Location":  # mortons-grille location
                    location_name = "".join(
                        search_sel.xpath(
                            '//div[@class="hero__content container"]/h1/text()'
                        )
                    ).strip()
                    country_code = "US"
                else:
                    country_code = formatted_addr.country

                if not country_code:
                    country_code = "CA"

                store_number = "<MISSING>"

                location_type = "<MISSING>"

                hours_of_operation = (
                    "; ".join(store.xpath("p")[-1].xpath(".//text()"))
                    .strip()
                    .replace("+", "")
                    .strip()
                )
                if (
                    hours_of_operation.replace("(", "")
                    .replace(")", "")
                    .replace("-", "")
                    .replace(" ", "")
                    .strip()
                    .isdigit()
                ):
                    hours_of_operation = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
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
