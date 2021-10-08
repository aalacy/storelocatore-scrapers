# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import time
from sgpostal import sgpostal as parser

website = "timhortonsgcc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    search_url = "https://timhortonsgcc.com/location/"
    with SgRequests(dont_retry_status_codes=([404]), verify_ssl=False) as session:
        search_res = session.get(search_url)
        search_sel = lxml.html.fromstring(search_res.text)
        map_url = "".join(
            search_sel.xpath('//a[.//span[text()="VIEW FULL MAP"]]/@href')
        ).strip()
        log.info(map_url)
        with SgChrome() as driver:
            driver.get(map_url)
            time.sleep(20)

            stores_resp = (
                driver.page_source.split('var _pageData = "')[1]
                .strip()
                .split('";</script>')[0]
                .strip()
                .replace('\\"', '"')
                .replace("\\/", "/")
                .strip()
            )
            stores = stores_resp.split('["Store Location",["')

            for index in range(1, len(stores)):
                page_url = search_url
                locator_domain = website
                location_name = (
                    stores[index].split('"]')[0].strip().replace("\\u0026", ",")
                )

                raw_address = (
                    stores[index]
                    .split('[["Store _ Address",["')[1]
                    .strip()
                    .split('"]')[0]
                    .strip()
                    .replace("\\n", ", ")
                    .strip()
                    .replace("\\u0026", ",")
                    .strip()
                    .replace("\\,", ",")
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
                country_code = formatted_addr.country

                store_number = "<MISSING>"

                phone = (
                    stores[index]
                    .split('["Store_ Phone",["')[1]
                    .strip()
                    .split('"]')[0]
                    .strip()
                    .replace("\\n", "\n")
                    .strip()
                )
                hours_of_operation = "<MISSING>"
                location_type = "<MISSING>"

                latlng = (
                    stores[index - 1].rsplit("[[[")[-1].strip().split("]]]")[0].strip()
                )
                latitude = latlng.split(",")[0].strip()
                longitude = latlng.split(",")[-1].strip()

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
