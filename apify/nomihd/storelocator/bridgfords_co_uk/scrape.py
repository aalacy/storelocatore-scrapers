# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.bridgfords.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bridgfords.co.uk/branches/"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        while True:
            search_res = session.get(search_url, headers=headers)
            search_sel = lxml.html.fromstring(search_res.text)

            stores = search_sel.xpath('//div[@class="card card--branch"]')

            for _, store in enumerate(stores[:-1]):

                page_url = "".join(store.xpath("./a/@href"))

                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                locator_domain = website
                store_json = (
                    store_res.text.split("data-location=")[1]
                    .split('<script type="application/ld+json">')[1]
                    .split("</script>")[0]
                    .strip()
                )
                store_info = json.loads(store_json)
                location_name = store_info["name"].strip()

                street_address = store_info["address"]["streetAddress"].strip()

                city = store_info["address"]["addressLocality"].strip()
                state = store_info["address"]["addressRegion"]
                zip = store_info["address"]["postalCode"].strip()

                country_code = "GB"

                store_number = page_url.split("/")[-2].strip()

                phone = store_info["telephone"]

                location_type = "".join(
                    store_sel.xpath('//input[@name="BranchType"]/@value')
                )
                hours = store_info["openingHoursSpecification"]
                hours_of_operation = "; ".join(hours).replace(":;", ":").strip()

                latitude, longitude = (
                    store_res.text.split("lat:")[1].split(",")[0].strip(),
                    store_res.text.split("lng:")[1].split("}")[0].strip(),
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

            next_page = "".join(
                search_sel.xpath('//div[@class="load-more load-more--lower"]//a/@href')
            ).strip()
            if len(next_page) <= 0:
                break
            search_url = "https://www.bridgfords.co.uk" + next_page
            log.info(search_url)


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
