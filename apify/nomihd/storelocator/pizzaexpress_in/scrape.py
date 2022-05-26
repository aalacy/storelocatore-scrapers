# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "pizzaexpress.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "api.urbanpiper.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "authorization": "apikey biz_adm_clients_fPGvPZNHfMeW:442b964aad46851f913ca8a718a9ec1bdf3aabff",
    "origin": "https://pizzaexpress.in",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "x-use-lang": "en",
}


def fetch_data():
    with SgRequests() as session:
        stores_req = session.get(
            "https://api.urbanpiper.com/api/v1/stores/",
            headers=headers,
        )
        stores = json.loads(stores_req.text)["stores"]

        for store in stores:
            page_url = "https://pizzaexpress.in/store-locator"
            locator_domain = website
            location_name = store["name"]
            if "Test Store" in location_name:
                continue

            raw_address = store["address"]
            if "#" in raw_address:
                raw_address = raw_address.split("#")[0].strip()

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

            if "-" in street_address.split(" ")[-1].strip():
                street_address = "".join(street_address.rsplit("-", 1)[0].strip())
            city = store["city"]
            state = "<MISSING>"
            zip = (
                raw_address.split(",")[-1]
                .strip()
                .split(" ")[-1]
                .strip()
                .replace(".", "")
                .strip()
            )
            if "-" in zip:
                zip = zip.split("-")[-1].strip()
            country_code = "IN"

            store_number = store["biz_location_id"]
            phone = store["phone"]

            location_type = "<MISSING>"
            if store["temporarily_closed"]:
                location_type = "temporarily closed"

            hours_list = []
            hours = store["time_slots"]
            days_list = []
            for hour in hours:
                if hour["day"] not in days_list:
                    days_list.append(hour["day"])
                    hours_list.append(
                        hour["day"]
                        + ":"
                        + hour["start_time"]
                        + " - "
                        + hour["end_time"]
                    )

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["lat"]
            longitude = store["lng"]

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
