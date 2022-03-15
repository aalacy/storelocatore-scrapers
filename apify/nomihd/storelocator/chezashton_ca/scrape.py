# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "chezashton.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://chezashton.ca/succursales/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    restaurant_list = search_sel.xpath('//ul[@class="restaurant__list"]/li')

    for restaurant in restaurant_list:

        page_url = search_url
        locator_domain = website

        location_name = "".join(restaurant.xpath("./@data-restaurant-title")).strip()

        xml_address = "".join(restaurant.xpath("./@data-restaurant-address")).strip()
        address_info = lxml.html.fromstring(xml_address)

        raw_address = " ".join(
            address_info.xpath('//p[not(contains(.//text(),"Téléphone"))]//text()')
        ).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country = "CA"
        country_code = country

        store_number = "<MISSING>"

        phone = "".join(
            address_info.xpath('//node()[contains(text(),"Téléphone")]//text()')
        ).strip()
        phone = phone.replace("Téléphone : ", "").strip()

        location_type = "<MISSING>"

        hours_of_operation = (
            "".join(restaurant.xpath("./@data-restaurant-opening"))
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("<span>", "")
            .replace("</span>", "")
            .strip()
        )

        hours_of_operation = "; ".join(hours_of_operation.split("\n")).strip()
        if "; Accessible" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("; Accessible")[0].strip()
        elif "; <br />Accessible" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("; <br />Accessible")[
                0
            ].strip()

        hours_of_operation = hours_of_operation.replace("\r", "").strip()
        latitude = "".join(restaurant.xpath("./@data-restaurant-lat")).strip()
        longitude = "".join(restaurant.xpath("./@data-restaurant-lng")).strip()

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
