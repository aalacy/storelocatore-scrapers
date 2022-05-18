# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "maxol.ie"
domain = "https://stations.maxol.ie/"
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
        store_sel.xpath('//h1/span[@class="LocationName"]/text()')
    ).strip()
    street_address = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]/address//span[@class="Address-field Address-line1"]/text()'
        )
    ).strip()

    add_2 = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]/address//span[@class="Address-field Address-line2"]/text()'
        )
    ).strip()

    if len(add_2) > 0:
        street_address = street_address + ", " + add_2

    city = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]/address//span[@class="Address-field Address-city"]/text()'
        )
    ).strip()

    state = "<MISSING>"

    zip = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]/address//span[@class="Address-field Address-postalCode"]/text()'
        )
    ).strip()

    country_code = "IE"

    store_number = "<MISSING>"
    phone = "".join(store_sel.xpath('//div[@itemprop="telephone"]/text()')).strip()
    location_type = "<MISSING>"
    latitude = store_sel.xpath(
        '//span[@class="Address-coordinates"]/meta[@itemprop="latitude"]/@content'
    )
    if len(latitude) > 0:
        latitude = latitude[0]

    longitude = store_sel.xpath(
        '//span[@class="Address-coordinates"][1]/meta[@itemprop="longitude"]/@content'
    )
    if len(longitude) > 0:
        longitude = longitude[0]

    hours = store_sel.xpath('//table[@class="c-hours-details"][1]')
    hours_list = []
    if len(hours) > 0:
        hours = hours[0].xpath("tbody/tr")
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]//text()")).strip()
            hours_list.append(day + ":" + time)

    hours_of_operation = "; ".join(hours_list).strip()

    return SgRecord(
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


def fetch_data():
    # Your scraper here
    states_sel = get_selector("https://stations.maxol.ie/index.html")
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
                    store_url = domain + "".join(city.xpath("@href")).strip()
                    store_sel = get_selector(store_url)
                    yield get_store_data(store_sel, store_url)

                else:
                    city_url = domain + "".join(city.xpath("@href")).strip()
                    stores_sel = get_selector(city_url)
                    stores = stores_sel.xpath('//a[@class="Teaser-titleLink"]/@href')

                    for store_url in stores:
                        page_url = (
                            domain
                            + store_url.replace("../", "")
                            .strip()
                            .replace("../", "")
                            .strip()
                        )
                        store_sel = get_selector(page_url)
                        yield get_store_data(store_sel, page_url)

            if len(cities) <= 0:
                stores = cities_sel.xpath('//a[@class="Teaser-titleLink"]/@href')
                for store_url in stores:
                    page_url = domain + store_url.replace("../", "").strip()
                    store_sel = get_selector(page_url)
                    yield get_store_data(store_sel, page_url)


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
