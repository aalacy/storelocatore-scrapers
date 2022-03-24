# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "lindt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_urls = [
        "https://www.lindt.ch/de/shops",
        "https://www.lindt.co.uk/stores/",
        "https://www.lindt.com.au/stores/",
        "https://www.lindt.at/stores/",
        "https://www.lindt.com.br/lojas-no-brasil",
        "https://www.lindt.bg/stores/",
        "https://www.lindt.cz/stores/",
        "https://www.lindt.fr/magasins/",
        "https://www.lindt.de/shops/",
        "https://www.lindt.hu/stores/",
        "https://www.lindt.it/stores/",
        "https://www.lindt-nordic.com/stores/",
        "https://www.lindt.pl/stores/",
        "https://www.lindt.ru/stores",
        "https://www.lindt.co.za/stores/",
        "https://www.lindt.es/tiendas-lindt/",
    ]

    with SgRequests() as session:

        for search_url in search_urls:

            log.info(search_url)
            search_res = session.get(search_url, headers=headers)
            if isinstance(search_res, SgRequestError):
                continue
            json_str = (
                search_res.text.split('"locationList":')[1].split("}]")[0].strip()
                + "}]}"
            )

            json_obj = json.loads(json_str)

            stores = json_obj["locationItems"]

            for no, store in enumerate(stores, 1):

                locator_domain = search_url.split("//")[1].split("/")[0]

                location_type = store["store_type"]

                page_url = search_url

                location_name = store["title"]

                if "Temporarily closed".upper() in location_name.upper():
                    location_type = "Temporarily Closed"

                raw_address = "<MISSING>"

                street_address = store["street"]

                city = store["city"]

                state = store["region"]
                zip = store["zip"]

                country_code = store["country_id"]
                if country_code == "US":
                    continue
                phone = store["phone"]

                hours = []
                for day in [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]:
                    if val := store[f"opening_hours_{day}"]:
                        hours.append(f"{day}: {val}")

                hours_of_operation = "; ".join(hours)

                store_number = store["location_id"]

                latitude, longitude = store["latitude"], store["longitude"]
                if latitude == longitude:
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
