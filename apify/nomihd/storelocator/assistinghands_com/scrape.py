# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape import sgpostal as parser

website = "assistinghands.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.assistinghands.com/location-finder/"
    search_res = session.get(search_url, headers=headers)

    stores_obj = json.loads(
        search_res.text.split("var wpgmaps_localize_marker_data =")[1]
        .strip()
        .split("};")[0]
        .strip()
        + "}"
    )

    for parent_key in stores_obj.keys():
        stores = stores_obj[parent_key]
        for key in stores.keys():
            store_sel = lxml.html.fromstring(stores[key]["desc"])
            page_url = "".join(
                store_sel.xpath('//a[contains(text(),"Visit Website")]/@href')
            ).strip()
            locator_domain = website

            location_name = stores[key]["title"]

            raw_address = stores[key]["address"]

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city

            if formatted_addr.state is not None:
                state = formatted_addr.state.replace(", Usa", "").strip()

            zip = formatted_addr.postcode

            country_code = "US"

            store_number = stores[key]["marker_id"]

            phone = "".join(
                store_sel.xpath('//p/a[contains(@href,"tel:")]//text()')
            ).strip()
            if len(phone) <= 0:
                phone = store_sel.xpath("//p//text()")
                if len(phone) > 0:
                    phone = phone[0].strip()

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = stores[key]["lat"]
            longitude = stores[key]["lng"]

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
