# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "bata.id"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        domain_API_dict = {
            "https://www.bata.id/storesfind": "https://www.bata.id/on/demandware.store/Sites-bata-id-Site/in_ID/Stores-FindStores?lat=1.7&long=104.0&radius=2100.0&userPositionLat=null&userPositionLong=null",
            "https://www.bata.co.th/storesfind": "https://www.bata.co.th/on/demandware.store/Sites-bata-th-Site/th_TH/Stores-FindStores?lat=1.7&long=104.0&radius=2100.0&userPositionLat=null&userPositionLong=null",
            "https://www.bata.in/storesfind?showMap=true&horizontalView=true&isForm=true": "https://www.bata.in/on/demandware.store/Sites-bata-in-Site/en_IN/Stores-FindStores?lat=21.0&long=78.0&radius=2100.0&userPositionLat=null&userPositionLong=null",
            "https://www.bata.com.my/storesfind": "https://www.bata.com.my/on/demandware.store/Sites-bata-my-Site/en_MY/Stores-FindStores?lat=1.7&long=104.0&radius=2100.0&userPositionLat=null&userPositionLong=null",
            "https://www.bata.it/negozi": "https://www.bata.it/on/demandware.store/Sites-bata-it-sfra-Site/it_IT/Stores-FindStores?lat=42.1119567&long=12.5217113&radius=660.0&userPositionLat=null&userPositionLong=null",
        }
        for key in domain_API_dict.keys():
            API_URL = domain_API_dict[key]
            stores_req = session.get(API_URL, headers=headers)
            stores = json.loads(stores_req.text)["stores"]
            for store in stores:

                store_number = store["ID"]
                page_url = key
                locator_domain = website

                location_name = store["name"]

                street_address = store["address"]

                city = store.get("city", "<MISSING>")
                state = store.get("district", "<MISSING>")
                zip = store.get("pCode", "<MISSING>")
                country_code = store.get("cCode", "<MISSING>")
                phone = store.get("phone", "<MISSING>")

                location_type = store.get("typeDV", "<MISSING>")
                hours_of_operation = store.get("hours", "<MISSING>")

                latitude = store.get("lat", "<MISSING>")
                longitude = store.get("long", "<MISSING>")

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
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.COUNTRY_CODE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
