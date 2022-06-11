# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "chrysler.cn"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "application/xml, text/xml, */*",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "http://chrysler.cn/dealer.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():
    # Your scraper here

    api_url = "http://chrysler.cn/js/dealer_new.xml"

    with SgRequests(verify_ssl=False) as session:
        api_res = session.get(api_url, headers=headers)
        stores_sel = lxml.html.fromstring(
            api_res.text.replace("<![CDATA[", "")
            .replace("]]>", "")
            .replace("<br>", "\n")
        )
        stores = stores_sel.xpath("//dealerlist/dealer")

        for store in stores:

            locator_domain = website

            location_name = "".join(store.xpath("./name/text()")).strip()
            page_url = "".join(store.xpath("./site/text()")).strip()
            if "建设中" in page_url:
                page_url = "http://chrysler.cn/dealer.html"

            location_type = "<MISSING>"

            raw_address = "".join(store.xpath("./address/text()")).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            city = "".join(store.xpath("./city/text()")).strip()
            state = "".join(store.xpath("./province/text()")).strip()
            zip = formatted_addr.postcode

            country_code = "CN"

            phone = (
                "".join(store.xpath("./phone/text()"))
                .strip()
                .replace("&mdash;", "-")
                .strip()
                .split(";")[0]
                .strip()
                .split("/")[0]
                .strip()
                .split(",")[0]
                .strip()
            )
            hours_of_operation = "<MISSING>"

            store_number = "".join(store.xpath("./id/text()")).strip()

            map_info = "".join(store.xpath("./map/text()")).strip()
            if map_info:
                latitude, longitude = map_info.split(",")[0], map_info.split(",")[1]
            else:
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
