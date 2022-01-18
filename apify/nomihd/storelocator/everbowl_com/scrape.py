# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "everbowl.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.everbowl.com/locations"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//div[@data-block-type="2" and @id and  .//a[contains(text(), "Click for map")]]'
    )

    for store in stores_list:

        page_url = search_url
        locator_domain = website

        location_name = (
            "".join(store.xpath(".//h2//text()")).strip().split(". ", 1)[1].strip()
        )
        if "COMING SOON" in location_name:
            continue

        address_info = list(filter(str, store.xpath(".//h3//text()")))
        if address_info[-1] == "—":
            raw_address = ", ".join(address_info[:-2]).strip()
            phone = address_info[-2]
        else:
            raw_address = ", ".join(address_info[:-1]).strip()
            phone = address_info[-1]

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        if "(" not in phone and "-" not in phone:
            phone = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        lat_lng_href = "".join(
            store.xpath('.//a[contains(text(), "Click for map")]/@href')
        )
        if "z/data=" in lat_lng_href:
            lat_lng = lat_lng_href.split("/@")[1].split("z/data")[0]
            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
        else:
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
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
