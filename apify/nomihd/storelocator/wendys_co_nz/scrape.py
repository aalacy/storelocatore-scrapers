# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import urllib.parse
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as BS

website = "wendys.co.nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.wendys.co.nz",
    "content-length": "0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "origin": "https://www.pizzahutcr.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.pizzahutcr.com/index/encuentrarestaurante",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.wendys.co.nz/store/maps"
    with SgRequests(verify_ssl=False) as session:
        search_res = session.get(search_url, headers=headers)
        json_str = search_res.text.split("JSON.parse('")[1].split("');")[0].strip()

        json_res = json.loads(json_str)

        store_list = json_res

        for store in store_list:

            page_url = "https://www.wendys.co.nz/store/" + store["slug"]
            locator_domain = website

            raw_address = (
                urllib.parse.unquote(store["address"]).strip().replace("\n", " ")
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "NZ"

            location_name = store["name"]

            phone = store["phone"]
            phone = urllib.parse.unquote(phone).strip()

            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours_info = urllib.parse.unquote(store["details"]).strip()
            hours = BS(hours_info, "lxml").get_text().split("\n")
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip().replace("\r", "").strip()) > 0:
                    hours_list.append(
                        "".join(hour)
                        .strip()
                        .replace("\r", "")
                        .strip()
                        .replace("\xa0", "")
                        .strip()
                    )
            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("CLOSED IN LEVEL 4;", "")
                .strip()
                .replace("(Regular hours", "")
                .strip()
                .replace(":;", "")
                .strip()
                .replace(";;", "")
                .strip()
                .replace(")", "")
                .strip()
            )
            latitude, longitude = (
                store["lat"],
                store["lng"],
            )

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
