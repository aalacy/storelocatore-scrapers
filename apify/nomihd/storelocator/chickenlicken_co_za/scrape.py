# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "chickenlicken.co.za"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "chickenlicken.co.za",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://chickenlicken.co.za/find-store",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://chickenlicken.co.za/find-store"
    cities = [
        "Johannesburg",
        "Vereeniging",
        "Pietermaritzburg",
        "Pretoria",
        "Durban",
        "Cape Town",
        "Welkom",
        "East London",
        "Randburg",
        "Roodepoort",
        "Port Elizabeth",
        "Bloemfontein",
        "Centurion",
        "Springs",
        "Sandton",
        "Polokwane",
        "Klerksdorp",
        "Rustenburg",
        "Kimberley",
        "Bhisho",
        "Benoni",
        "George",
        "Middelburg",
        "Vryheid",
        "Potchefstroom",
        "Umtata",
        "Brits",
        "Alberton",
        "Upington",
        "Paarl",
        "Queenstown",
        "Mmabatho",
        "Kroonstad",
        "Uitenhage",
        "Bethal",
        "Worcester",
        "Vanderbijlpark",
        "Grahamstown",
        "Standerton",
        "Brakpan",
        "Thohoyandou",
        "Saldanha",
        "Tzaneen",
        "Graaff-Reinet",
        "Oudtshoorn",
        "Mossel Bay",
        "Port Shepstone",
        "Knysna",
        "Vryburg",
        "Ladysmith",
        "Kuilsrivier",
        "Beaufort West",
        "Aliwal North",
        "Volksrust",
        "Musina",
        "Vredenburg",
        "Malmesbury",
        "Lebowakgomo",
        "Cradock",
        "De Aar",
        "Ulundi",
        "Jeffreyâ€™s Bay",
        "Lichtenburg",
        "Hermanus",
        "Carletonville",
        "Mahikeng",
        "Nelspruit",
    ]
    with SgRequests(dont_retry_status_codes=([404])) as session:
        for cit in cities:
            log.info(f"fetching data for city: {cit}")
            stores_req = session.get(
                "https://chickenlicken.co.za/api/v1/stores?filter[search]=" + cit,
                headers=headers,
            )
            if isinstance(stores_req, SgRequestError):
                continue
            stores = json.loads(stores_req.text)["data"]
            for store in stores:
                page_url = search_url
                locator_domain = website
                location_name = store["attributes"]["name"]
                raw_address = store["attributes"]["address"]
                if len(store["attributes"]["address2"]) > 0:
                    raw_address = raw_address + ", " + store["attributes"]["address2"]

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = store["attributes"]["area"]
                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = "ZA"
                store_number = store["id"]

                phone = store["attributes"]["telephone"]

                location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"
                latitude = store["attributes"]["latitude"]
                longitude = store["attributes"]["longitude"]
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
