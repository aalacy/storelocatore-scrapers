# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    urls = [
        "https://www.bathandbodyworks.mx/ubicacion-de-tiendas",
        "https://www.bathandbodyworks.gt/ubicacion-de-tiendas",
        "https://www.bathandbodyworks.pa/ubicacion-de-tiendas",
        "https://www.bathandbodyworks.pe/ubicacion-de-tiendas",
    ]

    with SgRequests() as session:
        for search_url in urls:
            headers = {
                "authority": search_url.split("https://")[1]
                .strip()
                .split("/")[0]
                .strip(),
                "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                "accept": "*/*",
                "rest-range": "resources=0-200",
                "content-type": "application/json; charset=utf-8",
                "sec-ch-ua-mobile": "?0",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
            }

            params = (
                (
                    "_fields",
                    "address,city,horario,latitude,longitude,name,neighborhood,phone,postalCode,state,storeSellerId",
                ),
                ("_sort", "name"),
            )

            API_URL = (
                search_url.split("/ubicacion-de-tiendas")[0].strip()
                + "/api/dataentities/SO/search?_fields=address,city,horario,latitude,longitude,name,neighborhood,phone,postalCode,state,storeSellerId&_sort=name"
            )
            search_res = session.get(API_URL, headers=headers, params=params)
            log.info(search_res)
            stores = search_res.json()
            for store in stores:
                page_url = search_url

                locator_domain = website

                location_name = store["name"]

                street_address = store["address"]
                city = store["city"]
                state = store["state"]
                zip = store["postalCode"]

                country_code = (
                    search_url.split("bathandbodyworks.")[1]
                    .strip()
                    .split("/")[0]
                    .strip()
                    .replace("com.", "")
                    .strip()
                )

                store_number = "<MISSING>"
                phone = store["phone"]

                location_type = "<MISSING>"

                hours_of_operation = store["horario"]

                latitude, longitude = (
                    store["latitude"].replace(",", ".").strip(),
                    store["longitude"].replace(",", ".").strip(),
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
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
