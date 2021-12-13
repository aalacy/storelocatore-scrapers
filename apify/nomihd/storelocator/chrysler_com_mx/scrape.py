# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

website = "chrysler.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.chrysler.com.mx",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.chrysler.com.mx/distribuidores",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.MEXICO],
            expected_search_radius_miles=15,
            max_search_results=None,
        )

        for lat, long in search:
            log.info(f"fetching data for coordinates: {lat},{long}")
            data = {"hidLatLongAuto": f"{lat},{long}"}

            search_res = session.post(
                "https://www.chrysler.com.mx/ajax/distribuidores-list/global",
                headers=headers,
                data=data,
            )
            try:
                search_sel = lxml.html.fromstring(search_res.text)
                stores = search_sel.xpath("//li")

                for store in stores:

                    locator_domain = website

                    location_name = "".join(
                        store.xpath("./div[@class='field nombredistexterno']//text()")
                    ).strip()

                    location_type = "<MISSING>"

                    raw_address = "<MISSING>"

                    street_address = "".join(
                        store.xpath("./div[@class='field calle']//text()")
                    ).strip()

                    city = "".join(
                        store.xpath("./div[@class='field colonia']//text()")
                    ).strip()

                    state = "".join(
                        store.xpath("./div[@class='field municipio']//text()")
                    ).strip()
                    zip = "".join(
                        store.xpath("./div[@class='field cp']//text()")
                    ).strip()

                    country_code = "MX"
                    phone = "".join(
                        store.xpath(".//a[contains(@href,'tel:')]//text()")
                    ).strip()

                    page_url = "".join(
                        store.xpath('./div[@class="field url"]/a/@href')
                    ).strip()

                    hours_of_operation = "<MISSING>"

                    store_number = "".join(store.xpath("./@data-value")).strip()

                    latitude, longitude = (
                        "".join(store.xpath("./@data-latitud")).strip(),
                        "".join(store.xpath("./@data-longitud")).strip(),
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
            except:
                pass


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
