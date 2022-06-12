# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "rockymountainurgentcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api_url = "https://rockymountainurgentcare.com/wp-admin/admin-ajax.php?action=store_search&lat=39.7392358&lng=-104.990251&max_results=1000&search_radius=5000&filter=8&autoload=1"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res

    for store in stores_list:

        page_url = "https://rockymountainurgentcare.com" + store["url"].strip()
        locator_domain = website

        location_name = store["store"].strip().replace("&#038;", "&")
        if "Cherry Creek" in location_name:
            page_url = page_url + "/locations/cherry-creek/"

        if "Boulder-Broadway" in location_name:
            continue  # available in json but not available on locator under urgent care

        street_address = store["address"].strip()
        if "address2" in store and store["address2"].strip():
            street_address = street_address + " " + store["address2"].strip()

        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["zip"].strip()

        country_code = "US"
        store_number = store["id"].strip()

        phone = store["phone"].strip()

        location_type = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        sections = store_sel.xpath(
            '//div[@class="siteorigin-widget-tinymce textwidget"]'
        )
        for sec in sections:
            if (
                "Urgent Care" in "".join(sec.xpath("h2//text()")).strip()
                or "Family Practice" in "".join(sec.xpath("h2//text()")).strip()
            ):
                phone = sec.xpath('p//a[contains(@href,"tel:")][1]/text()')
                if len(phone) > 0:
                    phone = phone[0]
                break

        hours_of_operation = "<MISSING>"
        text_sections = store_sel.xpath(
            '//div[@class="siteorigin-widget-tinymce textwidget"]/p'
        )
        for sec in text_sections:
            if (
                "Mon-" in "".join(sec.xpath(".//text()")).strip()
                or "Monday" in "".join(sec.xpath(".//text()")).strip()
            ):
                hours_of_operation = (
                    "; ".join(sec.xpath(".//text()"))
                    .strip()
                    .replace("\n", "")
                    .strip()
                    .replace("Hours:;", "")
                    .strip()
                )
                break

        latitude = store["lat"].strip()
        longitude = store["lng"].strip()

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
