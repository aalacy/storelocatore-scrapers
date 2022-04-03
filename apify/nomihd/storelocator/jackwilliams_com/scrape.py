# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "jackwilliams.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "jackwilliams.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "x-newrelic-id": "VgEBU1FSCBAFU1NbBQICX1U=",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://jackwilliams.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://jackwilliams.com/default/location",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        search_res = session.get(
            "https://jackwilliams.com/default/location", headers=headers
        )
        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath(
            '//a[contains(@href,"https://jackwilliams.com/default/location/")]/@href'
        )

        for store_url in store_list:

            page_url = store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            store_json = json.loads(
                "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]/text()')
                ).strip()
            )

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//div[@class="amlocator-block"]/h2/text()')
            ).strip()

            street_address = store_json["address"]["streetAddress"]

            city = store_json["address"]["addressLocality"]
            raw_address = store_sel.xpath('//p[@class="amlocator-text -bold"]/text()')
            state = (
                raw_address[-1]
                .split(",")[-1]
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", " ")
                .strip()
                .split(" ")[0]
                .strip()
            )
            store_number = store_json["address"]["addressRegion"]
            zip = store_json["address"]["postalCode"]
            country_code = "US"

            phone = store_json["telephone"]

            location_type = "<MISSING>"
            hours = store_json["openingHoursSpecification"]
            hours_list = []
            for hour in hours:
                opens = hour["opens"]
                closes = hour["closes"]
                if isinstance(hour["dayOfWeek"], list):
                    days_list = hour["dayOfWeek"]
                    for day in days_list:
                        hours_list.append(day + ": " + opens + " - " + closes)
                else:
                    day = hour["dayOfWeek"]
                    hours_list.append(day + ": " + opens + " - " + closes)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude, longitude = (
                store_json["geo"]["latitude"],
                store_json["geo"]["longitude"],
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
