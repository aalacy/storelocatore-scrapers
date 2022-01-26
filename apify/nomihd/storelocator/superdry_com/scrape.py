# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "https://superdry.com/"
domain = "https://stores.superdry.com/"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_selector(url):

    response = session.get(url, headers=headers)
    return lxml.html.fromstring(response.text)


def get_store_data(store_sel, page_url):

    log.info(page_url)
    locator_domain = website
    location_name = " ".join(
        store_sel.xpath(
            '//h1[@class="Hero-title"]//span[@class="LocationName"]//text()'
        )
    ).strip()
    street_address = "".join(
        store_sel.xpath(
            '//div[@class="Core-address"]//address//span[@class="c-address-street-1"]/text()'
        )
    ).strip()

    add_2 = "".join(
        store_sel.xpath(
            '//div[@class="Core-address"]//address//span[@class="c-address-street-2"]/text()'
        )
    ).strip()

    if len(add_2) > 0:
        street_address = street_address + ", " + add_2

    city = "".join(
        store_sel.xpath(
            '//div[@class="Core-address"]//address//span[@class="c-address-city"]/text()'
        )
    ).strip()

    state = "".join(
        store_sel.xpath(
            '//div[@class="Core-address"]//address//abbr[@class="c-address-state"]/text()'
        )
    ).strip()

    zip = "".join(
        store_sel.xpath(
            '//div[@class="Core-address"]//address//span[@class="c-address-postal-code"]/text()'
        )
    ).strip()

    raw_address = ""
    if len(street_address) > 0:
        raw_address = street_address

    if len(city) > 0:
        raw_address = raw_address + ", " + city

    if len(state) > 0:
        raw_address = raw_address + ", " + state

    if len(zip) > 0:
        raw_address = raw_address + ", " + zip

    country_code = "".join(
        store_sel.xpath('//abbr[@itemprop="addressCountry"]/text()')
    ).strip()
    store_number = "<MISSING>"
    phone = "".join(store_sel.xpath('//div[@itemprop="telephone"]/text()')).strip()
    location_type = "<MISSING>"
    if "head office" in location_name.lower():
        location_type = "Head Office"

    latitude = "".join(
        store_sel.xpath(
            '//div[contains(@class,"location-map-wrapper")]//meta[@itemprop="latitude"]/@content'
        )
    ).strip()
    longitude = "".join(
        store_sel.xpath(
            '//div[contains(@class,"location-map-wrapper")]//meta[@itemprop="longitude"]/@content'
        )
    ).strip()
    if len(latitude) <= 0:
        latitude = "".join(
            store_sel.xpath(
                '//span[@class="coordinates"]/meta[@itemprop="latitude"]/@content'
            )
        ).strip()
        longitude = "".join(
            store_sel.xpath(
                '//span[@class="coordinates"]/meta[@itemprop="longitude"]/@content'
            )
        ).strip()

    hours = store_sel.xpath(
        '//div[@class="c-hours"]//table[@class="c-hours-details"]/tbody/tr'
    )
    hours_list = []
    for hour in hours:
        day = "".join(hour.xpath("td[1]/text()")).strip()
        time = " ".join(hour.xpath("td[2]//text()")).strip()
        hours_list.append(day + ":" + time)

    hours_of_operation = "; ".join(hours_list).strip()

    store_output = SgRecord(
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
    return store_output


def fetch_data():
    # Your scraper here
    countries_sel = get_selector("https://stores.superdry.com/?view=storelocator")
    countries = countries_sel.xpath('//a[@class="Directory-listLink"]')
    count = 0
    for country in countries:
        count = count + int(
            "".join(country.xpath("@data-count"))
            .strip()
            .replace("(", "")
            .replace(")", "")
            .strip()
        )

        if "".join(country.xpath("@data-count")).strip() == "(1)":
            store_url = domain + "".join(country.xpath("@href")).strip()
            store_sel = get_selector(store_url)
            yield get_store_data(store_sel, store_url)
        else:
            country_url = domain + "".join(country.xpath("@href")).strip()
            states_sel = get_selector(country_url)
            states = states_sel.xpath('//a[@class="Directory-listLink"]')
            for state in states:
                if "".join(state.xpath("@data-count")).strip() == "(1)":
                    store_url = domain + "".join(state.xpath("@href")).strip()
                    store_sel = get_selector(store_url)
                    yield get_store_data(store_sel, store_url)

                else:
                    state_url = domain + "".join(state.xpath("@href")).strip()
                    cities_sel = get_selector(state_url)
                    cities = cities_sel.xpath('//a[@class="Directory-listLink"]')

                    for city in cities:
                        if "".join(city.xpath("@data-count")).strip() == "(1)":
                            stores = ["".join(city.xpath("@href")).strip()]
                        else:
                            city_url = domain + "".join(city.xpath("@href")).strip()
                            stores_sel = get_selector(city_url)
                            stores = stores_sel.xpath(
                                '//a[@class="Teaser-titleLink"]/@href'
                            )

                        for store_url in stores:
                            page_url = domain + store_url.replace("../", "").strip()
                            store_sel = get_selector(page_url)
                            yield get_store_data(store_sel, page_url)

                    if len(cities) <= 0:
                        stores = cities_sel.xpath(
                            '//a[@class="Teaser-titleLink"]/@href'
                        )

                        for store_url in stores:
                            page_url = domain + store_url.replace("../", "").strip()
                            store_sel = get_selector(page_url)
                            yield get_store_data(store_sel, page_url)

            if len(states) <= 0:
                stores = states_sel.xpath('//a[@class="Teaser-titleLink"]/@href')

                for store_url in stores:
                    page_url = domain + store_url.replace("../", "").strip()
                    store_sel = get_selector(page_url)
                    yield get_store_data(store_sel, page_url)

    log.info(f"total count should be: {count}")


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
