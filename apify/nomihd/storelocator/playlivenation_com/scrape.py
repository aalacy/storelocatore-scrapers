# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "playlivenation.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://playlivenation.com/?post_type=location&s=&state=0"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)
    store_list = search_sel.xpath(
        '//div[@id="locations-list"]//h2[text()="Upcoming Locations"]/preceding-sibling::article//div/a/@href'
    )

    for store in store_list:
        log.info(store)
        store_res = session.get(store, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        page_url = store
        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h1[@itemprop="name"]/text()')
        ).strip()
        street_address = ", ".join(
            store_sel.xpath(
                '//div[@class="address_wrapper"]//span[@itemprop="streetAddress"]/text()'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@class="address_wrapper"]//span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//div[@class="address_wrapper"]//span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//div[@class="address_wrapper"]//span[@itemprop="postalCode"]/text()'
            )
        ).strip()

        country_code = "US"
        store_number = "".join(store_sel.xpath('//input[@name="orgid"]/@value')).strip()

        location_type = (
            "Temporarily Closed"
            if store_sel.xpath(
                '//div[@id="loc-hours"]//span[contains(text(),"ly closed")]'
            )
            else "<MISSING>"
        )
        phone = "".join(
            store_sel.xpath(
                '//div[@class="phone_wrapper"]//span[@itemprop="telephone"]/text()'
            )
        ).strip()

        hours = store_sel.xpath(
            '//div[@id="loc-hours"]//span[@itemprop="openingHours"]'
        )
        hours_list = []
        for hour in hours:
            label = "".join(hour.xpath("@datetime")).strip().split(" ")[0].strip()
            if (
                "Mo" in label
                or "Tu" in label
                or "We" in label
                or "Th" in label
                or "Fr" in label
                or "Sa" in label
                or "Su" in label
            ):
                hours_list.append("".join(hour.xpath("text()")).strip())

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .replace("Thus location has reopened!; ", "")
            .strip()
        )

        lat_lng = (
            store_res.text.split("initMap() ")[1]
            .split("center: {")[1]
            .split("},")[0]
            .strip()
        )

        latitude = lat_lng.split(",")[0].replace("lat:", "").strip()
        longitude = lat_lng.split(",")[1].replace("lng:", "").strip()
        raw_address = "<MISSING>"
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
