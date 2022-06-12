# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "equinox.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.equinox.com"
    search_url = "https://www.equinox.com/clubs?icmp=topnav-clubs"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    json_str = "".join(search_sel.xpath('//script[@id="__NEXT_DATA__"]/text()'))

    json_res = json.loads(json_str)

    region_list = json_res["props"]["pageProps"]["allRegionData"]["items"][0]["fields"][
        "region"
    ]

    for region in region_list:

        subregion_list = region["fields"]["subRegions"]
        for subregion in subregion_list:

            store_list = subregion["fields"]["club"]
            for store in store_list:

                page_url = base + store["fields"]["clubDetailPageURL"]
                locator_domain = website
                log.info(page_url)
                page_res = session.get(page_url, headers=headers)
                page_sel = lxml.html.fromstring(page_res.text)

                store_json_str = "".join(
                    page_sel.xpath(
                        '//script[@data-type="club-detail-structured-data"]/text()'
                    )
                )
                if store_json_str:
                    store_obj = json.loads(store_json_str)

                    location_name = store["fields"]["webName"].strip()
                    street_address = store["fields"]["address"].strip()
                    city = store["fields"]["city"].strip()

                    state = store_obj["address"]["addressRegion"].strip()

                    zip = store["fields"]["zip"].strip()
                    country_code = store["fields"]["country"].strip()
                    store_number = store["fields"]["facilityId"]

                    phone = "".join(
                        list(
                            filter(
                                str,
                                page_sel.xpath('//a[contains(@href,"tel:")]//text()'),
                            )
                        )
                    )

                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    hours_obj = store_obj["openingHoursSpecification"]
                    if hours_obj:
                        hour_list = []
                        for obj in hours_obj:
                            day_of_week = obj["dayOfWeek"]
                            opens = obj["opens"]
                            closes = obj["closes"]

                            timing = f"{opens} - {closes}"
                            if "Invalid date" in timing:
                                timing = "Closed"

                            for day in day_of_week:
                                hour_list.append(f"{day}: {timing}")

                        hours_of_operation = "; ".join(hour_list)

                    else:
                        pass
                        # continue  # maybe LOCATION Coming soon

                    latitude = store_obj["geo"]["latitude"]
                    longitude = store_obj["geo"]["longitude"]

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
