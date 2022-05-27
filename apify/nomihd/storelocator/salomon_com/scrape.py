# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "salomon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "stores.salomon.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("lang", "en-us"),)


def fetch_data():
    # Your scraper here
    search_url = "https://stores.salomon.com/"
    stores_req = session.get(search_url, headers=headers, params=params)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = json.loads(
        stores_sel.xpath('//script[@type="application/ld+json"]/text()')[0]
    )
    for store in stores:
        page_url = store["url"]
        locator_domain = website
        location_name = store["name"]

        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip = store["address"]["postalCode"]
        store_number = "<MISSING>"
        phone = store["telephone"]

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        country_code = "".join(
            store_sel.xpath("//a[@data-country]/@data-country")
        ).strip()

        store_json = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        if len(store_json) > 0:
            store_json = json.loads(store_json[0])
            if not isinstance(store_json, dict):
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"
                slug = page_url.split("stores.salomon.com")[1].strip()
                location_type = (
                    "".join(
                        stores_sel.xpath(
                            f"//a[contains(@href,'{slug}')]/@data-categories"
                        )
                    )
                    .strip()
                    .split("|")[1]
                    .strip()
                )

            else:
                location_type = "".join(
                    store_sel.xpath('//div[@class="conv-section-badge"]/span/text()')
                ).strip()
                hours = store_json.get("openingHoursSpecification", [])
                hours_list = []
                for hour in hours:
                    days = hour["dayOfWeek"]
                    for d in days:
                        time = hour["opens"] + " - " + hour["closes"]
                        hours_list.append(d + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

                if "geo" in store_json:
                    latitude = store_json["geo"]["latitude"]
                    longitude = store_json["geo"]["longitude"]
                else:
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
