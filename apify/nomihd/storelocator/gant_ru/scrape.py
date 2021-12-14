# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gant.ru"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://gant.ru/adresa_magazinov/index.php"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        cities = search_sel.xpath('//select[@id="city-choise"]/option')

        for city_sel in cities:
            _city = "".join(city_sel.xpath(".//text()")).strip()
            city_id = "".join(city_sel.xpath("./@data-city"))

            stores = search_sel.xpath(f'.//div[@id="{city_id}"]//li[@id]')

            for no, store in enumerate(stores, 1):

                locator_domain = website

                location_name = "".join(store.xpath(".//h3//text()")).strip()

                page_url = search_url

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath('.//*[@itemprop="address"]//text()')
                        ],
                    )
                )
                raw_address = " ".join(store_info)

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
                    city = _city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "RU"

                phone = store.xpath('.//*[@itemprop="telephone"]//text()')
                if len(phone) > 0:
                    phone = phone[0].strip()
                else:
                    phone = "<MISSING>"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/*[@class="ct-contact--time"]//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = "; ".join(hours).replace("; :;", ":")

                store_number = "".join(store.xpath("./@id"))

                latitude, longitude = (
                    "".join(store.xpath(".//a/@data-lat")).replace("None", ""),
                    "".join(store.xpath(".//a/@data-lng")).replace("None", ""),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
