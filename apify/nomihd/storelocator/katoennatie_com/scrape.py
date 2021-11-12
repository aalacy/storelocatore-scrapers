# -*- coding: utf-8 -*-
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "katoennatie.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.katoennatie.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.katoennatie.com/locations/"
    with SgRequests() as session:

        stores_req = session.get(search_url, headers=headers)
        json_text = (
            stores_req.text.split("var locations = JSON.parse('")[1]
            .strip()
            .split("');")[0]
            .strip()
            .replace(',\\"', ',"')
            .replace('\\",', '",')
            .replace('\\":', '":')
            .replace(':\\"', ':"')
            .replace('{\\"', '{"')
            .replace('\\"}', '"}')
            .replace('\\"\\"', '""')
            .strip()
            .replace("\\'", "\\\\'")
        )
        stores = json.loads(json_text)

        for store in stores:

            page_url = "<MISSING>"
            location_type = "<MISSING>"
            locator_domain = website

            location_name = store["post_title"]

            raw_address = ""
            if len(store["post_content"]) > 0:
                add_sel = lxml.html.fromstring(store["post_content"])
                add_list = (
                    "".join(add_sel.xpath("//*//text()"))
                    .strip()
                    .replace("\\r\\n", ",")
                    .strip()
                    .split(",")
                )
                raw_address = []
                for add in add_list:
                    if len("".join(add).strip()) > 0:
                        if "http" in "".join(add).strip():
                            page_url = "".join(add).strip().replace("\\/", "/").strip()
                        else:
                            raw_address.append("".join(add).strip())
                raw_address = ", ".join(raw_address).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = formatted_addr.country

            phone = store["tel"]
            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            store_number = store["ID"]
            latitude, longitude = store["lat"], store["lng"]

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
