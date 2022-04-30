# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "gant.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.gant.co.uk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        API_URLs = [
            "https://www.gant.co.uk/stores",
            "https://www.gant.se/stores",
            "https://de.gant.com/stores",
            "https://nl.gant.com/stores",
            "https://fr.gant.com/stores",
            "https://dk.gant.com/stores",
            "https://es.gant.com/stores",
            "https://pt.gant.com/stores",
            "https://www.gant.be/nl_be/stores",
            "https://at.gant.com/stores",
            "https://ch.gant.com/stores",
        ]
        for index in range(0, len(API_URLs)):
            log.info(API_URLs[index])
            stores_req = session.get(
                API_URLs[index],
                headers=headers,
            )
            stores_sel = lxml.html.fromstring(stores_req.text)
            json_str = (
                "".join(stores_sel.xpath("//div[@data-locations]/@data-locations"))
                .strip()
                .replace("&quot;quot;", '"')
                .strip()
                .replace("&quot;", '"')
                .strip()
            )
            stores = json.loads(json_str)
            for store in stores:
                store_number = store["ID"]
                locator_domain = website
                page_url = API_URLs[index]
                location_name = store["name"]
                street_address = store.get("address1", "<MISSING>")
                if (
                    "address2" in store
                    and store["address2"] is not None
                    and len(store["address2"]) > 0
                ):
                    street_address = street_address + ", " + store["address2"]

                city = store.get("city", "<MISSING>")
                state = store.get("stateCode", "<MISSING>")
                zip = store.get("postalCode", "<MISSING>")
                country_code = store.get("countryCode", "<MISSING>")
                if location_name and location_name == "GANT Outlet Radolfzell":
                    street_address = store.get("city", "<MISSING>")
                    city = "Radolfzell"

                phone = store.get("phone", "<MISSING>")
                location_type = "<MISSING>"

                latitude = store.get("latitude", "<MISSING>")
                longitude = store.get("longitude", "<MISSING>")

                hours_list = []
                if "storeHours" in store:
                    hours = store["storeHours"]
                    for hour in hours:
                        hours_list.append(hour["day"] + ":" + hour["hours"])

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
