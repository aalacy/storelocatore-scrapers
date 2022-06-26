# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "yesss.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.yesss.co.uk",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.yesss.co.uk/branch-finder",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    api_url = "https://www.yesss.co.uk/branch-finder/location-data/all"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)

        stores = json_res["locations"]

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = store["url"]

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            location_name = store["name"].strip()

            location_type = store["ldSchema"]["@type"]

            raw_address = "<MISSING>"

            store_address = store["ldSchema"]["address"]

            street_address = store_address["streetAddress"]

            city = store_address["addressLocality"]

            state = store["addressLine4"]

            zip = store_address["postalCode"]
            country_code = store_address["addressCountry"]

            phone = store["phoneNumber"]

            store_json_str = store_res.text.split(
                '<script type="application/ld+json">'
            )[1].split("</script>")[0]

            store_json = json.loads(store_json_str)

            hours_info = store_json["openingHoursSpecification"]
            hour_list = []
            for hour_info in hours_info:
                opens = hour_info["opens"]
                closes = hour_info["closes"]
                weekdays = hour_info["dayOfWeek"]
                if weekdays is not None:
                    for day in weekdays:
                        if opens != closes:

                            hour_list.append(f"{day}: {opens}-{closes}")
                        else:
                            hour_list.append(f"{day}: Closed")

            hours_of_operation = "; ".join(hour_list).replace(":;", ":")
            store_number = store["id"]

            latitude, longitude = store["latitude"], store["longitude"]
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
