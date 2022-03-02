# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "fineandcountry.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fineandcountry.com/uk/find-an-estate-agent"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            search_url,
            headers=headers,
        )
        stores = stores_req.text.split("codeAddress(")[2:]
        for index in range(0, len(stores)):

            page_url = search_url
            locator_domain = website
            json_str = (
                "{" + stores[index].split(");")[0].strip().split("{", 1)[1].strip()
            )
            store_json = json.loads(json_str)

            location_name = store_json["officeName"]

            add_list = []
            if len(store_json["addressName"]) > 0:
                add_list.append(store_json["addressName"])

            if len(store_json["addressNumber"]) > 0:
                add_list.append(store_json["addressNumber"])

            if len(store_json["addressStreet"]) > 0:
                add_list.append(store_json["addressStreet"])

            if len(store_json["address2"]) > 0:
                add_list.append(store_json["address2"])

            if len(store_json["address3"]) > 0:
                add_list.append(store_json["address3"])

            if len(store_json["address4"]) > 0:
                add_list.append(store_json["address4"])

            if len(store_json["addressPostcode"]) > 0:
                add_list.append(store_json["addressPostcode"])

            if len(store_json["country"]) > 0:
                add_list.append(store_json["country"])

            raw_address = ", ".join(add_list).strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = store_json["addressPostcode"]
            if zip:
                if zip == "PO Box 346016":
                    street_address = "PO Box 346016"
                    zip = "<MISSING>"

                if zip.replace("/", "").strip().replace(" ", "").strip().isalpha():
                    zip = "<MISSING>"

                if zip == "WA 6005":
                    zip = "6005"

                if zip == ".":
                    zip = "<MISSING>"

                if location_name == "Fine & Country Costa Blanca North":
                    zip = "03700"

            country_code = store_json["country"]

            store_number = store_json["officeID"]

            location_type = "<MISSING>"
            phone = store_json["rsContactNumber"]
            if phone:
                phone = phone.split("/")[0].strip()

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store_json["lat"],
                store_json["long"],
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
