# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mideast.chrysler.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.mideast.chrysler.com/en/find-a-dealer.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        json_str = (
            search_res.text.split('data-component="News" data-props="')[1]
            .split('"></div>')[0]
            .strip()
        )
        json_str = json_str.replace("&#34;", '"')
        json_res = json.loads(json_str)
        stores = json_res["newsData"]["filterableList"]["newsitems"]["newsContent"]

        for store in stores:
            is_loc_name_missing = False
            locator_domain = website

            location_name = store["bannerDetails"]["title"]["value"]
            if len(location_name) <= 0:
                is_loc_name_missing = True
            page_url = search_url
            location_type = "<MISSING>"

            country_code = store["bannerDetails"]["preTitle"]["value"]

            sub_stores_str = (
                store["bannerDetails"]["postTitle"]["value"]
                .replace("&amp;lt;", "<")
                .replace("&amp;gt;", ">")
            )

            sub_stores_sel = lxml.html.fromstring(sub_stores_str)
            sub_store_list = sub_stores_sel.xpath("//span[@style]")
            for sub_idx, sub_store in enumerate(sub_store_list, 1):
                info = list(
                    filter(str, [x.strip() for x in sub_store.xpath(".//text()")])
                )
                info = " ".join(info)
                phone = info.split("Phone")[1].strip()

                raw_address = info.split("Phone")[0].strip()

                if is_loc_name_missing:
                    location_name = raw_address.split(" ")[0].strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                if zip:
                    zip = zip.replace("-40M", "").strip()
                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.PHONE,
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
