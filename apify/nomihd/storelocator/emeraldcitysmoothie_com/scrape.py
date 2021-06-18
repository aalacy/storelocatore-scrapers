# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgzip.dynamic import DynamicZipSearch, Grain_2

website = "emeraldcitysmoothie.com"
logger = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=None,
    granularity=Grain_2(),
)


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


def fetch_data():
    for zipcode in search:
        logger.info(f"pulling records for zipcode: {zipcode}")
        search_url = f"https://www.emeraldcitysmoothie.com/api/locations?filter=true&per_page=100&address={zipcode}&page=1"
        stores_req = session.get(search_url.format(zipcode), headers=headers)
        if "data" in stores_req.text:
            if stores_req.status_code == 200:
                json_data = json.loads(stores_req.text.replace("\n", "").strip())[
                    "data"
                ]
                for stores in json_data:

                    if len(stores) > 0 and isinstance(stores, dict):
                        if stores["url"] not in url_list:
                            url_list.append(stores["url"])
                            page_url = stores["url"]
                            logger.info(f"Page URL: {page_url}")
                            locator_domain = website
                            location_name = stores["name"]
                            street_address = stores["address"]["address1"]
                            if (
                                stores["address"]["address2"] is not None
                                and len(stores["address"]["address2"]) > 0
                            ):
                                street_address = (
                                    street_address
                                    + ", "
                                    + stores["address"]["address2"]
                                )

                            city = stores["address"]["city"]
                            state = stores["address"]["state"]
                            zip = stores["address"]["zip"]
                            country_code = "US"

                            store_number = str(stores["id"])
                            logger.info(f"Store Number: {store_number}")
                            phone = stores["phone"]
                            location_type = "<MISSING>"
                            hours_of_operation = (
                                stores["hours"]
                                .replace("<p>", "")
                                .replace("</p>", "")
                                .replace("<br>", "; ")
                                .replace("\n", "; ")
                                .replace("&nbsp", "")
                                .strip()
                                .replace(";; ", "; ")
                                .rstrip(";")
                            )

                            latitude = stores["address"]["lat"]
                            longitude = stores["address"]["lng"]
                            search.found_location_at(latitude, longitude)
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
                                logger.info(page_url)
                                locator_domain = website
                                location_name = store["name"]
                                street_address = store["address"]["address1"]
                                if (
                                    store["address"]["address2"] is not None
                                    and len(store["address"]["address2"]) > 0
                                ):
                                    street_address = (
                                        street_address
                                        + ", "
                                        + store["address"]["address2"]
                                    )
                                logger.info(f"Street Address: {street_address}")
                                city = store["address"]["city"]
                                state = store["address"]["state"]
                                zip = store["address"]["zip"]
                                country_code = "US"

                                store_number = str(store["id"])
                                logger.info(f"Store Number: {store_number}")
                                phone = store["phone"]

                                location_type = "<MISSING>"
                                hours_of_operation = (
                                    store["hours"]
                                    .replace("<p>", "")
                                    .replace("</p>", "")
                                    .replace("<br>", "; ")
                                    .replace("\n", "; ")
                                    .replace("&nbsp", "")
                                    .strip()
                                    .replace(";; ", "; ")
                                    .rstrip(";")
                                )

                                latitude = store["address"]["lat"]
                                longitude = store["address"]["lng"]
                                search.found_location_at(latitude, longitude)
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
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
