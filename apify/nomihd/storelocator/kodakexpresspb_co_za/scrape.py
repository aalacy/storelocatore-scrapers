# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "kodakexpresspb.co.za"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "http://www.kodakexpresspb.co.za/store-location"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        json_str = search_res.text.split('"markers":')[1].split(',"directionsText"')[0]
        stores = json.loads(json_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            store_html = store["content"].strip(" \n").strip()
            store_sel = lxml.html.fromstring(store_html)

            page_url = search_url

            location_name = store["title"].strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(str, [x.strip() for x in store_sel.xpath("//p//text()")])
            )

            raw_address = ", ".join(store_info[1:]).split("Tel:")[0].strip(", ").strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city
            if not city:
                city = raw_address.split(",")[-1].strip()

            state = formatted_addr.state

            zip = formatted_addr.postcode

            country_code = "ZA"

            phone = store_info[-2].split("Tel:")[1].strip()

            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            latitude, longitude = store["lat"], store["lng"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
