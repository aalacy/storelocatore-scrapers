# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mariasitaliankitchen.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://mariasitaliankitchen.com/locations/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//section//div[h3]")

        for no, store in enumerate(stores, 1):

            locator_domain = website
            store_number = "<MISSING>"

            page_url = search_url

            location_name = "".join(store.xpath("./h3//text()")).strip()
            if location_name == "Catering":
                continue

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p//text()")],
                )
            )

            for gm_idx, x in enumerate(store_info):
                if "GM:" in x:
                    break

            if "GM:" in store_info[gm_idx]:
                phone = store_info[gm_idx].split("GM:")[1].split("\n")[1].strip()
            else:
                phone = "<MISSING>"

            raw_address = (
                ", ".join(store_info)
                .split("GM:")[0]
                .strip()
                .replace("\n", ", ")
                .strip()
            )

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city

            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            for hour_idx, x in enumerate(store_info):
                if "Hours:" in x:
                    break

            if "Hours:" in store_info[hour_idx]:

                hours_of_operation = (
                    "; ".join(store_info[hour_idx + 1 :])
                    .replace("day; ", "day: ")
                    .replace("day:;", "day:")
                    .replace("OPEN FOR BUSINESS!", "")
                    .replace("NOW OPEN!", "")
                    .replace("\n", "")
                    .strip()
                    .strip(";! ")
                )
                hours_of_operation = hours_of_operation.split("Will be")[0].strip(" ;")
            else:
                hours_of_operation = "<MISSING>"

            latitude, longitude = "<MISSING>", "<MISSING>"

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
