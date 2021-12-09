# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "footlocker.fr"
domain = "https://stores.footlocker.fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_selector(url, session):

    try:
        response = SgRequests.raise_on_err(session.get(url, headers=headers))
        return lxml.html.fromstring(response.text)
    except SgRequestError:
        pass


def get_store_data(store_sel, page_url):

    log.info(page_url)
    locator_domain = website
    location_name = " ".join(
        store_sel.xpath(
            '//h1[@class="c-location-title"]/span[@class="location-name-geo"]/text()'
        )
    ).strip()
    street_address = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address//span[@class="c-address-street-1"]/text()'
        )
    ).strip()

    add_2 = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address//span[@class="c-address-street-2"]/text()'
        )
    ).strip()

    if len(add_2) > 0:
        street_address = street_address + ", " + add_2

    city = (
        "".join(
            store_sel.xpath(
                '//section[@class="nap-unit-inner"]//address//span[@class="c-address-city"]/text()'
            )
        )
        .strip()
        .replace("(kids)", "")
        .strip()
    )

    state = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address//abbr[@class="c-address-state"]/text()'
        )
    ).strip()

    zip = "".join(
        store_sel.xpath(
            '//section[@class="nap-unit-inner"]//address//span[@class="c-address-postal-code"]/text()'
        )
    ).strip()

    country_code = store_sel.xpath(
        '//section[@class="nap-unit-inner"]//address//abbr[@itemprop="addressCountry"]/text()'
    )
    if len(country_code) > 0:
        country_code = country_code[0]

    store_number = "<MISSING>"
    phone = "".join(store_sel.xpath('//span[@itemprop="telephone"]/text()')).strip()
    location_type = "<MISSING>"

    latitude = store_sel.xpath(
        '//span[@class="coordinates"]/meta[@itemprop="latitude"]/@content'
    )
    if len(latitude) > 0:
        latitude = latitude[0]

    longitude = store_sel.xpath(
        '//span[@class="coordinates"][1]/meta[@itemprop="longitude"]/@content'
    )
    if len(longitude) > 0:
        longitude = longitude[0]

    hours = store_sel.xpath('//table[@class="c-location-hours-details"][1]')
    if len(hours) > 0:
        hours = hours[0].xpath("tbody/tr")
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time_list = hour.xpath("td[2]/span")
            final_time_list = []
            for t in time_list:
                final_time_list.append("".join(t.xpath(".//text()")).strip())

            if len(final_time_list) <= 0:
                final_time_list.append("".join(hour.xpath("td[2]//text()")).strip())
            time = ", ".join(final_time_list)
            hours_list.append(day + ":" + time)

    hours_of_operation = "; ".join(hours_list).strip()
    if hours_of_operation.encode("ascii", "ignore").decode("utf-8").count("Ferm") == 7:
        location_type = "Temporary Closed"
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


def fetch_data(session):
    # Your scraper here
    temp_sel = get_selector(
        "https://stores.footlocker.fr/fr/lyon/112-cours-charlemagne.html", session
    )
    if temp_sel:
        yield get_store_data(
            temp_sel, "https://stores.footlocker.fr/fr/lyon/112-cours-charlemagne.html"
        )
    states_sel = get_selector("https://stores.footlocker.fr/fr/index.html", session)
    states = states_sel.xpath('//li[@class="c-directory-list-content-item"]')
    for state in states:
        if (
            "".join(
                state.xpath("span[@class='c-directory-list-content-item-count']/text()")
            ).strip()
            == "(1)"
        ):
            store_url = (
                domain
                + "".join(state.xpath("a/@href")).strip().replace("..", "").strip()
            )
            store_sel_1 = get_selector(store_url, session)
            if store_sel_1:
                yield get_store_data(store_sel_1, store_url)

        else:
            state_url = (
                domain
                + "".join(state.xpath("a/@href")).strip().replace("..", "").strip()
            )
            stores_sel = get_selector(state_url, session)
            stores = stores_sel.xpath('//article[@class="LocationCard"]')

            for store_url in stores:
                page_url = (
                    domain
                    + "".join(
                        store_url.xpath('.//a[@class="LocationCard-title--link"]/@href')
                    )
                    .replace("..", "")
                    .strip()
                )
                store_sel = get_selector(page_url, session)
                if store_sel:
                    yield get_store_data(store_sel, page_url)
                else:
                    street_address = "".join(
                        store_url.xpath(
                            './/address//span[@class="c-address-street-1"]/text()'
                        )
                    ).strip()
                    add_2 = "".join(
                        store_url.xpath(
                            './/address//span[@class="c-address-street-2"]/text()'
                        )
                    ).strip()

                    if len(add_2) > 0:
                        street_address = street_address + ", " + add_2

                    city = "".join(
                        store_url.xpath(
                            './/address//span[@class="c-address-city"]/text()'
                        )
                    ).strip()

                    state = "".join(
                        store_url.xpath(
                            './/address//abbr[@class="c-address-state"]/text()'
                        )
                    ).strip()

                    zip = "".join(
                        store_url.xpath(
                            './/address//span[@class="c-address-postal-code"]/text()'
                        )
                    ).strip()
                    country_code = store_url.xpath(
                        './/address//abbr[contains(@class,"c-address-country-name")]/text()'
                    )
                    if len(country_code) > 0:
                        country_code = country_code[0]

                    yield SgRecord(
                        locator_domain=website,
                        page_url="<MISSING>",
                        location_name="".join(
                            store_url.xpath(
                                './/a[@class="LocationCard-title--link"]/text()'
                            )
                        ).strip(),
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
                        country_code=country_code,
                        store_number="<MISSING>",
                        phone="".join(
                            store_url.xpath(
                                './/span[@class="c-phone-number-span c-phone-main-number-span"]/text()'
                            )
                        ).strip(),
                        location_type="<MISSING>",
                        latitude="<MISSING>",
                        longitude="<MISSING>",
                        hours_of_operation="09:30 - 20:00",
                    )


def scrape():
    log.info("Started")
    count = 0
    session = SgRequests()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data(session)
        for rec in results:
            if rec:
                writer.write_row(rec)
                count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
