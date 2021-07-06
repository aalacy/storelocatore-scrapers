# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "acceptanceinsurance.com"
domain = "https://locations.acceptanceinsurance.com/"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_store_links(x):
    if domain in x:
        if x.count("/") > 5:
            return True

    return False


def fetch_data():
    # Your scraper here
    response = session.get(domain, headers=headers)
    states = (
        response.text.split('"significantLink":')[1]
        .split("]")[0]
        .strip(" []")
        .split(",")
    )
    states = [x.strip(' "') for x in states]

    for state in states:
        log.info(state)
        state_res = session.get(state, headers=headers)
        stores = (
            state_res.text.split('"significantLink":')[1]
            .split("]")[0]
            .strip(" []")
            .split(",")
        )
        stores = [x.strip(' "') for x in list(filter(get_store_links, stores))]

        for store in stores:
            log.info(store)
            store_res = session.get(store, headers=headers)
            if store_res.ok is False:
                continue
            json_str = (
                store_res.text.split('<script type="application/ld+json">')[1]
                .split("</script>")[0]
                .strip()
            )
            json_obj = json.loads(json_str)

            locator_domain = website
            page_url = store

            location_name = (
                json_obj["name"] + " - " + json_obj["address"]["streetAddress"]
            )
            street_address = json_obj["address"]["streetAddress"]
            city = json_obj["address"]["addressLocality"]
            state = json_obj["address"]["addressRegion"]
            zip = json_obj["address"]["postalCode"]
            country_code = json_obj["address"]["addressCountry"]
            store_number = json_obj["branchCode"]
            phone = json_obj["telephone"]
            location_type = "<MISSING>"
            hour_list = json_obj["openingHours"]
            hours_of_operation = "; ".join(hour_list)

            latitude = json_obj["geo"]["latitude"]
            longitude = json_obj["geo"]["longitude"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
