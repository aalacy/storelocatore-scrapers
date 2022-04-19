# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mainevent.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.mainevent.com/site-map/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="w-64 lg:text-center"]/a/@href')
        for store_url in stores:
            page_url = "https://www.mainevent.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            if isinstance(store_req, SgRequestError) or "Coming soon" in store_req.text:
                continue
            store_sel = lxml.html.fromstring(store_req.text)
            json_text = "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
            if len(json_text) > 0:
                store_json = json.loads(json_text)

                locator_domain = website
                location_name = store_json["name"]
                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]
                country_code = store_json["address"]["addressCountry"]

                store_number = ""
                try:
                    store_number = (
                        store_req.text.split('\\"qubicaCenterId\\":\\"')[1]
                        .strip()
                        .split('\\"')[0]
                        .strip()
                    )
                except:
                    pass

                phone = store_json["telephone"]

                location_type = "<MISSING>"

                latitude = ""
                try:
                    latitude = (
                        store_req.text.split('\\"latitude\\":')[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )
                except:
                    pass

                longitude = ""
                try:
                    longitude = (
                        store_req.text.split('\\"longitude\\":')[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )
                except:
                    pass

                hours_of_operation = ""
                hours = store_json["openingHoursSpecification"]
                hours_list = []
                for hour in hours:
                    time = hour["opens"] + "-" + hour["closes"]
                    if isinstance(hour["dayOfWeek"], str):
                        day = hour["dayOfWeek"]
                        hours_list.append(day + ":" + time)
                    else:
                        days = hour["dayOfWeek"]
                        for day in days:
                            hours_list.append(day + ":" + time)

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
