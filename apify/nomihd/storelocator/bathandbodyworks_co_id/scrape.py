# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "bathandbodyworks.co.id"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    urls = [
        "https://www.bathandbodyworks.co.id/store-locator",
        "https://www.bathandbodyworks.com.my/store-locator",
        "https://www.bathandbodyworks.com.sg/store-locator",
        "https://www.bathandbodyworks.co.th/store-locator",
    ]

    with SgRequests() as session:
        for search_url in urls:
            country_code = (
                search_url.split("bathandbodyworks.")[1]
                .strip()
                .split("/")[0]
                .strip()
                .replace("com.", "")
                .strip()
                .replace("co.", "")
                .strip()
            )
            headers = {
                "authority": "api.storepoint.co",
                "cache-control": "max-age=0",
                "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "sec-fetch-site": "none",
                "sec-fetch-mode": "navigate",
                "sec-fetch-user": "?1",
                "sec-fetch-dest": "document",
                "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
            }

            tag = ""
            if country_code == "id":
                tag = "indonesia"
            elif country_code == "my":
                tag = "malaysia"
            elif country_code == "sg":
                tag = "singapore"
            elif country_code == "th":
                tag = "thailand"

            log.info(tag)
            search_res = session.get(
                "https://api.storepoint.co/v1/15eb1315885175/locations?rq&tags[]={}".format(
                    tag
                ),
                headers=headers,
            )
            log.info(search_res)
            stores = search_res.json()["results"]["locations"]
            for store in stores:
                page_url = search_url

                locator_domain = website

                location_name = store["name"]

                raw_address = store["streetaddress"]
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                store_number = store["id"]
                phone = store["phone"]

                location_type = "<MISSING>"

                hours_of_operation = (
                    store["description"]
                    .replace("\n", "; ")
                    .strip()
                    .replace("Hours:", "")
                    .strip()
                )

                latitude, longitude = (
                    store["loc_lat"],
                    store["loc_long"],
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
