# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "eyreandelliston.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.eyreandelliston.co.uk",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.eyreandelliston.co.uk/branches"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        json_str = (
            search_res.text.split("var initialStockists = ")[1]
            .split("</script>")[0]
            .strip()
        )
        stores = json.loads(json_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url + "/" + store["alias"]

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = store["name"].strip()

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            store_address = store["address"]

            street_address = (
                (store_address["address1"] + "," + store_address["address2"])
                .strip()
                .strip(", ")
            )

            city = store_address["address3"]

            state = store_address["county"]

            zip = store_address["postcode"]
            country_code = "GB"

            phone = store["telephone"]

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[h3="Opening Hours"]//tr//text()'
                        )
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours).replace(":;", ":").replace("day;", "day:")
            )
            store_number = store["id"]

            latitude, longitude = store["location"]["lat"], store["location"]["lng"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
