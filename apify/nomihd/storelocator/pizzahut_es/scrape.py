# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl
import json
from urllib.parse import quote

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "pizzahut.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Referer": "https://www.pizzahut.es/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.es/pizzerias"
    with SgChrome() as driver:
        driver.get(search_url)
        provinces_sel = lxml.html.fromstring(driver.page_source)
        provinces = provinces_sel.xpath(
            '//div[@data-testid="store-localizator__container--provinces"]//a'
        )
        for prov in provinces:
            prov_url = "https://www.pizzahut.es" + quote(
                "".join(prov.xpath("@href")).strip()
            )
            state = "".join(prov.xpath("text()")).strip()
            log.info(prov_url)
            driver.get(prov_url)

            cities_sel = lxml.html.fromstring(driver.page_source)
            cities = cities_sel.xpath(
                '//div[@data-testid="store-localizator__container--cities"]//a'
            )
            for cit in cities:
                temp_city = "".join(cit.xpath("text()")).strip()
                temp_city = quote(temp_city)
                city_url = f"https://www.pizzahut.es/api/stores/cities/{temp_city}"
                log.info(city_url)
                driver.get(city_url)
                stores_sel = lxml.html.fromstring(driver.page_source)
                stores = json.loads("".join(stores_sel.xpath("//body//text()")).strip())
                for store in stores:
                    ID = store["id"]
                    driver.get(f"https://www.pizzahut.es/api/stores/{ID}")
                    store_sel = lxml.html.fromstring(driver.page_source)
                    store_json = json.loads(
                        "".join(store_sel.xpath("//body//text()")).strip()
                    )
                    store_number = store_json["externalStoreId"]
                    location_name = store_json["name"]

                    slug = store_json["alias"]
                    slug = quote(slug)
                    page_url = f"https://www.pizzahut.es/pizzerias/store/{slug}"
                    log.info(page_url)
                    driver.get(page_url)
                    store_page_sel = lxml.html.fromstring(driver.page_source)
                    locator_domain = website

                    street_address = (
                        store_json["street"] + " " + store_json["streetNumber"]
                    )
                    city = store_json["city"]
                    if not city:
                        city = temp_city

                    zip = (
                        "".join(
                            store_page_sel.xpath(
                                '//div[@data-testid="store-details__container--store-address"]/text()'
                            )
                        )
                        .strip()
                        .split(" ")[-1]
                        .strip()
                    )

                    country_code = "ES"

                    phone = store_json["phoneNumber"]
                    if phone and phone == "0":
                        phone = "<MISSING>"

                    location_type = "<MISSING>"
                    hours = store_page_sel.xpath(
                        '//div[@data-testid="store-details__container--opening-hours-pickup"]//div[contains(@class,"opening-hour-row")]'
                    )
                    hours_list = []
                    for hour in hours:
                        day = "".join(hour.xpath("div[1]//text()")).strip()
                        time = ", ".join(
                            list(
                                filter(
                                    str,
                                    [x.strip() for x in hour.xpath("div[2]//text()")],
                                )
                            )
                        ).strip()
                        hours_list.append(day + ":" + time)

                    hours_of_operation = "; ".join(hours_list).strip()
                    log.info(hours_of_operation)
                    latitude = store_json["latitude"]
                    longitude = store_json["longitude"]

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
