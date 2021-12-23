# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.fridays.com.my"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "http://www.fridays.com.my/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        cities = search_sel.xpath(
            '//ul[@class="sub-menu"]/li[contains(a/@href,"/find-us/")]'
        )

        for city in cities:
            city_url = "".join(city.xpath("./a/@href"))
            log.info(city_url)
            city_res = session.get(city_url, headers=headers)
            city_sel = lxml.html.fromstring(city_res.text)

            stores = city_sel.xpath('//div[@class="toggler extralight-border"]')

            for _, store in enumerate(stores, 1):

                page_url = city_url

                locator_domain = website

                location_name = "".join(store.xpath(".//text()")).strip()
                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './following-sibling::div[@class="toggle_wrap"][1]//text()'
                            )
                        ],
                    )
                )

                raw_address = (
                    " ".join(store_info)
                    .split("Tel")[0]
                    .split("Email")[0]
                    .strip()
                    .strip(". ")
                    .strip()
                )
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = formatted_addr.country
                if not country_code:
                    country_code = "MY"

                store_number = "<MISSING>"

                phone = " ".join(store_info).split("Email")[0].split("Tel:")[1].strip()

                location_type = "<MISSING>"

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
