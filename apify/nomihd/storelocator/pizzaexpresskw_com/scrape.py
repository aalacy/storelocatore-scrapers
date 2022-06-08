# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzaexpresskw.com"
domain = "https://www.pizzaexpresskw.com/"
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
        store_sel.xpath('//div[@class="Hero-name"]/text()')
        + store_sel.xpath('//div[@class="Hero-geomodifier js-alt-font"]/text()')
    )
    street_address = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]//address//span[@class="Address-field Address-line1"]/text()'
        )
    ).strip()

    add_2 = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]//address//span[@class="Address-field Address-line2"]/text()'
        )
    ).strip()

    if len(add_2) > 0:
        street_address = street_address + ", " + add_2

    city = "".join(
        store_sel.xpath(
            '//div[@class="Address Core-address"]//address//span[@class="Address-field Address-city"]/text()'
        )
    ).strip()

    state = ""
    zip = ""

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
        store_sel.xpath('//span[@itemprop="addressCountry"]/text()')
    ).strip()
    store_number = "<MISSING>"
    phone = "".join(store_sel.xpath('//span[@itemprop="telephone"]/text()')).strip()
    location_type = "<MISSING>"

    latitude = "".join(
        store_sel.xpath(
            '//span[@class="Address-coordinates"]//meta[@itemprop="latitude"]/@content'
        )
    ).strip()
    longitude = "".join(
        store_sel.xpath(
            '//span[@class="Address-coordinates"]//meta[@itemprop="longitude"]/@content'
        )
    ).strip()
    hours = store_sel.xpath(
        '//div[@class="c-hours"]//table[@class="c-hours-details"]/tbody/tr'
    )
    hours_list = []
    for hour in hours:
        day = "".join(hour.xpath("td[1]/text()")).strip()
        time = "".join(hour.xpath("td[2]//text()")).strip()
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
    countries_sel = get_selector("https://www.pizzaexpresskw.com/directory")
    countries = countries_sel.xpath('//a[@class="Directory-listLink"]')
    for country in countries:
        country_url = domain + "".join(country.xpath("@href")).strip()
        log.info(country_url)
        states_sel = get_selector(country_url)
        states = states_sel.xpath('//a[@class="Directory-listLink"]')
        for state in states:
            state_url = (
                domain
                + "".join(state.xpath("@href")).strip().replace("../", "").strip()
            )
            log.info(state_url)
            cities_sel = get_selector(state_url)
            stores = cities_sel.xpath('//a[@class="Teaser-cardLink"]/@href')
            for store_url in stores:
                page_url = domain + store_url.replace("../", "").strip()
                log.info(page_url)
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
