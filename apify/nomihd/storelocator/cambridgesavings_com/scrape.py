# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "cambridgesavings.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.cambridgesavings.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    markers = stores_sel.xpath('//div[@class="geolocation-location js-hide"]')
    lat_lng_dict = {}
    for marker in markers:
        map_url = "".join(marker.xpath('.//h2[@class="field-content"]/a/@href')).strip()
        lat = "".join(marker.xpath("@data-lat")).strip()
        lng = "".join(marker.xpath("@data-lng")).strip()
        lat_lng_dict[map_url] = lat + "," + lng

    stores = stores_sel.xpath('//div[contains(@class,"view-location-branches")]//li')
    for store in stores:
        page_url = (
            "https://www.cambridgesavings.com"
            + "".join(
                store.xpath('.//a[contains(text(),"Branch Details")]/@href')
            ).strip()
        )

        location_name = "".join(
            store.xpath(
                ".//h3[@class='c-heading c-heading--l4 u-mb12 u-color-black']/text()"
            )
        ).strip()
        location_type = "<MISSING>"
        locator_domain = website
        phone = "".join(store.xpath('.//*[contains(@href,"tel:")]/text()')).strip()

        street_address = "".join(
            store.xpath('.//address/span[@class="address-line1"]/text()')
        ).strip()

        street_address_2 = "".join(
            store.xpath('.//address/span[@class="address-line2"]/text()')
        ).strip()
        if len(street_address_2) > 0:
            street_address = street_address_2

        city = "".join(store.xpath('.//address/span[@class="locality"]/text()')).strip()
        state = "".join(
            store.xpath('.//address/span[@class="administrative-area"]/text()')
        ).strip()
        zipp = "".join(
            store.xpath('.//address/span[@class="postal-code"]/text()')
        ).strip()

        hours_list = []
        hours = store.xpath('.//table[@class="o-table u-text-left u-12/12@md"]/tr')
        for hour in hours:
            day = "".join(hour.xpath("th/text()")).strip()
            time = "".join(hour.xpath("td[1]/text()")).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()
        country_code = "US"
        store_number = "<MISSING>"

        map_link = "".join(
            store.xpath('.//a[contains(text(),"View on Map")]/@href')
        ).strip()
        latitude = lat_lng_dict[map_link].split(",")[0].strip()
        longitude = lat_lng_dict[map_link].split(",")[-1].strip()

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
