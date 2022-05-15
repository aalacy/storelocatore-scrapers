# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.gant.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.gant.com.tr"
    search_url = "https://www.gant.com.tr/stores/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        cities = search_sel.xpath('//div[contains(@class,"stores-city-group-wrapper")]')
        for city_sel in cities:

            stores = city_sel.xpath('.//div[@class="stores__list__item"]')

            for store in stores:

                locator_domain = website

                location_name = "".join(store.xpath(".//a//text()")).strip()

                page_url = base + "".join(store.xpath(".//a/@data-content-url"))
                log.info(page_url)

                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[contains(@class,"stores__list")]//address//text()'
                            )
                        ],
                    )
                )
                raw_address = ", ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                if not city:
                    temp_city = city_sel.xpath("./div//text()")
                    if len(temp_city) > 0:
                        city = temp_city[0]

                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "TR"

                phone = "".join(
                    store_sel.xpath(
                        '//div[contains(@class,"stores__list")]//a[contains(@href,"tel:")]//text()'
                    )
                )
                if len(phone) < 5:
                    phone = "<MISSING>"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//div[contains(@class,"stores__list")]/div/p[contains(@class,"store-detail-address-text")]//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = "; ".join(hours).replace("; :;", ":")

                store_number = page_url.split("/")[-2]

                latitude, longitude = (
                    "".join(store_sel.xpath('//div[@id="map"]/@data-lat')).replace(
                        "None", ""
                    ),
                    "".join(store_sel.xpath('//div[@id="map"]/@data-lng')).replace(
                        "None", ""
                    ),
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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
