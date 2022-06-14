# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "gingin.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "gingin.mx",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://gingin.mx/ubicaciones/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//div[@class='wpb_wrapper'][./div[1]/div[1][h2]]")

        for store in stores:

            locator_domain = website

            page_url = search_url
            location_name = "".join(
                store.xpath(
                    "div[@class='wpb_text_column wpb_content_element ']/div/h2/text()"
                )
            ).strip()

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p/text()")],
                )
            )
            if len(store_info) == 1:
                continue
            location_type = "<MISSING>"

            raw_address = store_info[1]
            formatted_addr = parser.parse_address_intl(raw_address)

            street_address = raw_address.split(",")[0].strip()
            city = formatted_addr.city
            if city:
                city = city.split(" Cdmx")[0].strip()

            state = formatted_addr.state

            zip = raw_address.split(",")[-2].strip().split(" ")[0].strip()

            country_code = "MX"

            store_number = "<MISSING>"

            phone = store_info[0].strip().replace("Teléfono", "").strip()

            hours_of_operation = "".join(store_info[-1]).strip()

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
