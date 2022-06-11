# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

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
    for stat in states:
        log.info(stat)
        state_res = session.get(stat, headers=headers)
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
                temp_url = store.replace(
                    "https://locations.acceptanceinsurance.com", ""
                ).strip()
                page_url = stat + temp_url.split("/")[2].strip()
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                page_url = page_url
                curr_store = store_sel.xpath(
                    f'//div[@id="location-list"]//div[@class="location-detail row"][.//strong[@class="name"]/a[contains(@href,"{temp_url}")]]'
                )
                if len(curr_store) > 0:
                    curr_store = curr_store[0]
                    location_name = "".join(
                        curr_store.xpath('.//strong[@class="name"]//text()')
                    ).strip()
                    street_address = "".join(
                        curr_store.xpath('.//div[@class="street"]/text()')
                    ).strip()
                    city_state = "".join(
                        curr_store.xpath('.//div[@class="locality"]/text()')
                    ).strip()
                    city = city_state.split(",")[0].strip()

                    state = city_state.split(",")[-1].strip()

                    zip = "".join(
                        curr_store.xpath('.//div[@class="locality"]/span/text()')
                    ).strip()
                    country_code = "US"
                    store_number = "".join(
                        store_sel.xpath(
                            f'//div[@id="location-list"][.//strong[@class="name"]/a[contains(@href,"{temp_url}")]]/@data-currentlocation'
                        )
                    ).strip()

                    phone = "".join(
                        curr_store.xpath('.//div[@class="telephone"]//text()')
                    ).strip()
                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"

                    map_link = "".join(
                        curr_store.xpath('.//a[contains(@href,"maps/dir")]/@href')
                    ).strip()
                    latitude = ""
                    longitude = ""
                    if len(map_link) > 0:
                        latitude = map_link.split("/")[-1].strip().split(",")[0].strip()
                        longitude = (
                            map_link.split("/")[-1].strip().split(",")[-1].strip()
                        )

                    yield SgRecord(
                        locator_domain=website,
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

            else:
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
