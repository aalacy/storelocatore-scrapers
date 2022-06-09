# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "cncc.com/carte-de-france-interactive-des-centres-commerciaux"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "us-central1-sad-interactive.cloudfunctions.net",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://sad-interactive.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://sad-interactive.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

data = '[{"id":14,"value":["Existant"]}]'


def fetch_data():
    # Your scraper here

    with SgRequests() as session:
        search_res = session.post(
            "https://us-central1-sad-interactive.cloudfunctions.net/cncc_filter_poi_prod",
            headers=headers,
            data=data,
        )

        stores = json.loads(search_res.text)["poi_id"]

        for store in stores:
            locator_domain = website
            store_number = store["id"]
            page_url = f"https://us-central1-sad-interactive.cloudfunctions.net/cncc_poi_prod?id={store_number}"
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if isinstance(store_req, SgRequestError):
                continue

            store_json = json.loads(store_req.text)
            attributes = store_json["attribut"]
            location_type = "<MISSING>"
            location_name = "<MISSING>"
            for att in attributes:
                if att["libelle"] == "Type de Centre":
                    location_type = att["valeur"]
                if att["libelle"] == "Site":
                    location_name = att["valeur"]
                if att["libelle"] == "Site Web":
                    page_url = att["valeur"]

            street_address = store_json["address"]
            city = store_json["city"]
            state = "<MISSING>"
            zip = store_json["posta_code"]
            country_code = store_json["country"]

            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            latitude, longitude = store["lat"], store["lng"]

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
