# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "havaianas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://us.havaianas.com/front/app/store/search?execution=e1s1"
    search_res = session.get(search_url, headers=headers)

    json_text = (
        search_res.text.split("storeProcessor.renderStore();")[1]
        .split("})(")[1]
        .split("</script>")[0]
        .split("}]}")[0]
        + "}]}"
    )
    json_body = json.loads(json_text)

    for state, stores_list in json_body.items():
        for store in stores_list:

            page_url = search_url
            locator_domain = website

            location_name = store["store"]["name"]

            street_address = store["store"]["address"]["address1"]

            if (
                "address2" in store["store"]["address"]
                and store["store"]["address"]["address2"] is not None
                and len(store["store"]["address"]["address2"]) > 0
            ):
                street_address = (
                    street_address + ", " + store["store"]["address"]["address2"]
                )
            if (
                "address3" in store["store"]["address"]
                and store["store"]["address"]["address3"] is not None
                and len(store["store"]["address"]["address3"]) > 0
            ):
                street_address = (
                    street_address + ", " + store["store"]["address"]["address3"]
                )

            city = store["store"]["address"]["city"]
            state = store["store"]["address"]["province"]
            zip = store["store"]["address"]["postalCode"]

            country_code = store["store"]["address"]["country"]

            store_number = store["store"]["storeId"]

            phone = store["store"]["phoneNumber"]

            location_type = "<MISSING>"

            hours_of_operation = (
                store["store"]["hours"]
                .replace("<br>", "")
                .replace("\n", "; ")
                .replace("Hours:", "")
                .strip(" ;")
            )

            latitude = store["store"]["latitude"]
            longitude = store["store"]["longitude"]

            raw_address = "<MISSING>"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
