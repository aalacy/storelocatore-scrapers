# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "simplymac.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://api2.storepoint.co/v1/15ec82b1d81806/locations?rq"
    stores_req = session.get(search_url, headers=headers)
    if json.loads(stores_req.text)["success"] is True:
        stores = json.loads(stores_req.text)["results"]["locations"]

        for store in stores:
            page_url = store["website"]
            locator_domain = website
            location_name = store["name"]

            raw_address = store["streetaddress"].replace(
                "3275 N Reserve St Unit B Missoula MT59808",
                "3275 N Reserve St Unit B, Missoula, MT 59808",
            )
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"
            store_number = str(store["id"])
            phone = store["phone"]
            location_type = store["description"]
            hours_list = []
            if len(store["monday"]) > 0:
                hours_list.append("monday:" + store["monday"])
            else:
                hours_list.append("monday:" + "Closed")
            if len(store["tuesday"]) > 0:
                hours_list.append("tuesday:" + store["tuesday"])
            else:
                hours_list.append("tuesday:" + "Closed")
            if len(store["wednesday"]) > 0:
                hours_list.append("wednesday:" + store["wednesday"])
            else:
                hours_list.append("wednesday:" + "Closed")
            if len(store["thursday"]) > 0:
                hours_list.append("thursday:" + store["thursday"])
            else:
                hours_list.append("thursday:" + "Closed")
            if len(store["friday"]) > 0:
                hours_list.append("friday:" + store["friday"])
            else:
                hours_list.append("friday:" + "Closed")
            if len(store["saturday"]) > 0:
                hours_list.append("saturday:" + store["saturday"])
            else:
                hours_list.append("saturday:" + "Closed")
            if len(store["sunday"]) > 0:
                hours_list.append("sunday:" + store["sunday"])
            else:
                hours_list.append("sunday:" + "Closed")

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["loc_lat"]
            longitude = store["loc_long"]
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

    else:
        log.error("Something wrong with the response SUCCESS value")


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
