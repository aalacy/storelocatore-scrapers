# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from lxml import etree
from sgscrape import sgpostal as parser

website = "vanellisrestaurants.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://vanellisrestaurants.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = etree.fromstring(stores_req.text)
    stores = stores_sel.xpath("//store/item")
    for store in stores:
        page_url = ""
        locator_domain = website
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zip = ""
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        full_raw_address = ""
        for child in store:
            if child.tag == "latitude":
                latitude = child.text
            if child.tag == "longitude":
                longitude = child.text
            if child.tag == "storeId":
                store_number = child.text
            if child.tag == "exturl":
                page_url = child.text
            if child.tag == "telephone":
                phone = child.text
            if child.tag == "location":
                location_name = child.text.replace("&amp;", "&").strip()
            if child.tag == "address":
                raw_address = child.text.replace("&#44;", ",").strip()
                full_raw_address = raw_address
                state_zip = raw_address.rsplit(",", 1)[-1].strip()
                state = state_zip.split(" ", 1)[0].strip()
                zip = state_zip.split(" ", 1)[-1].strip()
                raw_address = ", ".join(raw_address.rsplit(",", 1)[:-1]).strip()
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                if city is None and location_name == "Place du Royaume":
                    city = "Chicoutimi"

                country_code = "CA"

            if child.tag == "operatingHours":
                hours_of_operation = child.text

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
            raw_address=full_raw_address,
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
