# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "happyjoes.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "storerocket.io",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://storerocket.io/api/user/Ly8GR5rJr0/locations", headers=headers
        )
        stores = json.loads(stores_req.text)["results"]["locations"]
        for store in stores:
            if store["visible"] != 1:
                continue
            locator_domain = website
            location_name = store["name"]
            street_address = store["address_line_1"]
            if len(store["address_line_2"]) > 0:
                street_address = street_address + ", " + store["address_line_2"]

            if street_address:
                street_address = (
                    street_address.replace("Southridge Plaza ", "")
                    .strip()
                    .replace("Dubuque, IA 52001", "")
                    .strip()
                    .replace(" Muscatine", "")
                    .strip()
                )

            raw_address = street_address
            city = store["city"]
            if city:
                raw_address = raw_address + ", " + city

            state = store["state"]
            if state:
                raw_address = raw_address + ", " + state

            zip = store["postcode"]
            if zip:
                raw_address = raw_address + ", " + zip

            formatted_addr = parser.parse_address_intl(raw_address)
            city = formatted_addr.city
            if not city:
                city = location_name.split(" ")[0].strip()

            country_code = store["country"]

            store_number = store["id"]
            phone = store["phone"]
            if not phone:
                continue
            location_type = store["locationType"]["name"]
            slug = store["slug"]

            page_url = f"https://happyjoes.com/locations/{state.lower()}/{slug}/"
            latitude = store["lat"]
            longitude = store["lng"]
            hours = store["hours"]
            hours_list = []
            for d in hours.keys():
                if hours[d] and hours[d] != "Missing":
                    hours_list.append(d + ":" + hours[d])

            hours_of_operation = "; ".join(hours_list).strip()

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
