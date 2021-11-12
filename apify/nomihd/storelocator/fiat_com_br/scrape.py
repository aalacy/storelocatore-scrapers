# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "fiat.com.br"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    urls_list = [
        "https://dealer-service.k8s.fcalatam.com.br/dealerws/dealer?brandId=0&market=pt-BR&showBlocked=false&loadAll=true&latitude=-23.5557714&longitude=-46.6395571&radius=10000",
        "https://dealer-service.k8s.fcalatam.com.br/dealerws/dealer?brandId=0&market=es-AR&showBlocked=false&loadAll=true&latitude=-28.788986275685975&longitude=-77.38852213508977&radius=8959",
    ]
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        for search_url in urls_list:
            log.info(search_url)
            search_res = session.get(search_url, headers=headers)
            stores = json.loads(search_res.text)
            for store in stores:
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["fantasyName"]

                phone = store["telephone"]
                street_address = store["address"]
                city = store["city"]["name"]
                state = store["state"]
                zip = "<MISSING>"

                country_code = (
                    search_url.split("market=")[1]
                    .strip()
                    .split("-")[1]
                    .strip()
                    .split("&")[0]
                    .strip()
                )

                store_number = store["dealerCode"]
                location_type = store["brandsName"]

                hours_of_operation = "<MISSING>"
                latitude, longitude = store["latitude"], store["longitude"]
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
