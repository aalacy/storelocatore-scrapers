# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

website = "emeraldcitysmoothie.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.emeraldcitysmoothie.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.emeraldcitysmoothie.com/locations?address=98001&page=1",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

url_list = []


def fetch_records_for(zipcode):
    log.info(f"pulling records for zipcode: {zipcode}")
    search_url = "https://www.emeraldcitysmoothie.com/api/locations?filter=true&per_page=100&address={}&page=1"

    stores_req = session.get(search_url.format(zipcode), headers=headers)
    if "data" in stores_req.text:
        stores = json.loads(stores_req.text.replace("\n", "").strip())["data"]
        yield stores


def process_record(raw_results_from_one_zipcode):
    for stores in raw_results_from_one_zipcode:
        if len(stores) > 0 and isinstance(stores, dict):
            for key in stores.keys():
                if stores[key]["url"] not in url_list:
                    url_list.append(stores[key]["url"])
                    page_url = stores[key]["url"]
                    log.info(page_url)
                    locator_domain = website
                    location_name = stores[key]["name"]
                    street_address = stores[key]["address"]["address1"]
                    if (
                        stores[key]["address"]["address2"] is not None
                        and len(stores[key]["address"]["address2"]) > 0
                    ):
                        street_address = (
                            street_address + ", " + stores[key]["address"]["address2"]
                        )

                    city = stores[key]["address"]["city"]
                    state = stores[key]["address"]["state"]
                    zip = stores[key]["address"]["zip"]
                    country_code = "US"

                    store_number = str(stores[key]["id"])
                    phone = stores[key]["phone"]

                    location_type = "<MISSING>"
                    hours_of_operation = (
                        stores[key]["hours"]
                        .replace("<p>", "")
                        .replace("</p>", "")
                        .replace("<br>", "; ")
                        .strip()
                    )

                    latitude = stores[key]["address"]["lat"]
                    longitude = stores[key]["address"]["lng"]

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
                    )

        elif len(stores) > 0 and isinstance(stores, list):
            for store in stores:
                if store["url"] not in url_list:
                    url_list.append(store["url"])
                    page_url = store["url"]
                    log.info(page_url)
                    locator_domain = website
                    location_name = store["name"]
                    street_address = store["address"]["address1"]
                    if (
                        store["address"]["address2"] is not None
                        and len(store["address"]["address2"]) > 0
                    ):
                        street_address = (
                            street_address + ", " + store["address"]["address2"]
                        )

                    city = store["address"]["city"]
                    state = store["address"]["state"]
                    zip = store["address"]["zip"]
                    country_code = "US"

                    store_number = str(store["id"])
                    phone = store["phone"]

                    location_type = "<MISSING>"
                    hours_of_operation = (
                        store["hours"]
                        .replace("<p>", "")
                        .replace("</p>", "")
                        .replace("<br>", "; ")
                        .strip()
                    )

                    latitude = store["address"]["lat"]
                    longitude = store["address"]["lng"]

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
                    )


def scrape():
    log.info("Started")
    with SgWriter() as writer:
        results = parallelize(
            search_space=static_zipcode_list(
                radius=20, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=32,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
