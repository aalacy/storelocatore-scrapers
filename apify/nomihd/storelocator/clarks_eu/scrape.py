# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "clarks.eu"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "Referer": "https://www.clarks.eu/at/en/",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.clarks.eu/at/en/store-locator"
    with SgRequests() as session:
        countries_req = session.get(search_url, headers=headers)
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath(
            '//select[@id="dwfrm_storelocator_address_country"]/option[position()>1]/@value'
        )
        for country in countries:
            stores_URL = f"https://www.clarks.eu/on/demandware.store/Sites-clarks-Site/en_US/Stores-FindByCountryOnly?countryCode={country}"
            log.info(stores_URL)
            stores_req = session.get(stores_URL, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//ul[@class="b-storelocator-results_list"]/li')
            for store in stores:
                page_url = "https://www.clarks.eu/es/en/store-locator"

                locator_domain = website
                location_name = "".join(
                    store.xpath(".//h3[@class='b-storelocator-store_name']/text()")
                ).strip()
                street_address = ", ".join(
                    store.xpath(
                        './/div[@class="b-storelocator-store_info"]/div[@class="b-storelocator-store_address"]/span/text()'
                    )
                ).strip()

                city_zip = "".join(
                    store.xpath(".//span[@class='b-storelocator-store_city']/text()")
                ).strip()
                city = city_zip.split(",")[0].strip()
                state = "<MISSING>"
                zip = city_zip.split(",")[-1].strip()
                phone = (
                    "".join(
                        store.xpath(
                            ".//div[@class='b-storelocator-store_phone']/text()"
                        )
                    )
                    .strip()
                    .replace("Phone:", "")
                    .strip()
                )
                street_address = street_address.split(zip)[0].strip()
                if len(street_address) > 0 and street_address[-1] == ",":
                    street_address = "".join(street_address[:-1]).strip()

                country_code = country
                store_number = "".join(store.xpath(".//a/@data-id")).strip()

                location_type = "<MISSING>"

                latitude = "".join(store.xpath(".//a/@data-latitude")).strip()
                longitude = "".join(store.xpath(".//a/@data-longitude")).strip()

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
