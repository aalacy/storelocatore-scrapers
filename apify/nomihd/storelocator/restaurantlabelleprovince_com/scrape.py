# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape import sgpostal as parser


website = "restaurantlabelleprovince.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "http://restaurantlabelleprovince.com/fr/les-succursales/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    api_url = "http://restaurantlabelleprovince.com/ext/loadAllMarkers.php"
    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    restaurants_list = json_res["obFin"]
    for restaurant in restaurants_list:

        page_url = search_url
        locator_domain = website

        raw_address = restaurant["address"]

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        raw_street1 = raw_address.split(",", 2)[0]
        raw_street2 = raw_address.split(",", 2)[1]

        city = restaurant["city"].strip()

        location_name = "".join(
            search_sel.xpath(
                f'//table[@id="tblMenu"]//p[contains(text(),"{raw_street1}")]/parent::node()//h3/text()'
            )
        ).strip()

        if location_name == "":
            location_name = "".join(
                search_sel.xpath(
                    f'//table[@id="tblMenu"]//node()[contains(text(),"{city}")]/parent::node()//h3/text()'
                )
            ).strip()

        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "CA"

        store_number = restaurant["id"]

        phone = search_sel.xpath(
            f'//table[@id="tblMenu"]//p[contains(text(),"{raw_street1}")]/text()'
        )

        if not phone:
            phone = search_sel.xpath(
                f'//table[@id="tblMenu"]//node()[contains(text(),"{city}")]/parent::node()//p/text()'
            )

        if phone:
            phone = phone[-1].strip()

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = restaurant["lat"]
        longitude = restaurant["lng"]

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
            raw_address=", ".join(raw_address.split("\n")),
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
