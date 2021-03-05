# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "beerknurd.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.beerknurd.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//div[@class="field-content"]/a/@href')
    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@class="page-header"]/text()')
        ).strip()

        street_address = "".join(
            store_sel.xpath('//div[@class="street-block"]/div/text()')
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@class="addressfield-container-inline locality-block country-US"]/span[@class="locality"]/text()'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//div[@class="addressfield-container-inline locality-block country-US"]/span[@class="state"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//div[@class="addressfield-container-inline locality-block country-US"]/span[@class="postal-code"]/text()'
            )
        ).strip()

        country_code = "US"

        phone = "".join(
            store_sel.xpath(
                '//div[@class="field field-name-field-phone-number field-type-text field-label-hidden"]/div/div/text()'
            )
        ).strip()

        hours = store_sel.xpath(
            '//div[@class="field field-name-field-hours field-type-text-long field-label-hidden"]/div/div/p/text()'
        ) + store_sel.xpath(
            '//div[@class="field field-name-field-hours field-type-text-long field-label-hidden"]/div/div/span/text()'
        )

        hours_list = []
        for hour in hours:
            if (
                "am" in "".join(hour).strip().lower()
                or "pm" in "".join(hour).strip().lower()
            ):
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
        try:
            hours_of_operation = hours_of_operation.split("-Social Hour")[0].strip()
        except:
            pass

        store_number = "<MISSING>"

        latitude = ""
        longitude = ""
        try:
            map_link = (
                store_req.text.split("maps/embed?")[1].strip().split('"')[0].strip()
            )
            if len(map_link) > 0:
                latitude = map_link.split("!1d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            pass

        if len(location_name) > 0:
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
        # break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
