# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser

website = "saintcinnamon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.saintcinnamon.com/locations.html"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    raw_locations_data_list = search_sel.xpath("//table//tr//p[not( .//strong)]/text()")

    raw_locations = list(
        filter(str, [raw_data.strip() for raw_data in raw_locations_data_list])
    )

    raw_locations_str = " ".join(raw_locations)

    locations_list = list(
        map(
            lambda x: ("Saint Cinnamo" + x).strip(),
            raw_locations_str.split("Saint Cinnamo")[1:],
        )
    )

    for location in locations_list:
        page_url = search_url
        locator_domain = website

        raw_address = location.replace(" at", "").replace(
            "Saint Cinnamon Bake Shoppe", ""
        )

        location_name = "Saint Cinnamon Bake Shoppe"

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = (
            "CA"
            if ("Indonesia" not in location and "Philippines" not in location)
            else "IN"
            if "Indonesia" in location
            else "PH"
        )
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        phone = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
