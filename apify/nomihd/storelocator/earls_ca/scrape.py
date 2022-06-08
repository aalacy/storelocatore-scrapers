# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "earls.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://earls.ca/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    json_str = (
        search_res.text.split("var allLocations = ")[1].split("</script>")[0].strip()
    )
    json_str = json_str.replace("name:", "'name':")
    json_str = json_str.replace("address1:", "'address1':")
    json_str = json_str.replace("address2:", "'address2':")
    json_str = json_str.replace("phone:", "'phone':")
    json_str = json_str.replace("image:", "'image':")
    json_str = json_str.replace("smallImage:", "'smallImage':")
    json_str = json_str.replace("slug:", "'slug':")
    json_str = json_str.replace("id:", "'id':")
    json_str = json_str.replace("lat:", "'lat':")
    json_str = json_str.replace("long:", "'long':")
    json_str = json_str.replace("ready:", "'ready':")
    json_str = json_str.replace(
        "orderingNotAvailableTitle:", "'orderingNotAvailableTitle':"
    )
    json_str = json_str.replace(
        "orderingNotAvailableBody:", "'orderingNotAvailableBody':"
    )
    json_str = json_str.replace("isEventSpace:", "'isEventSpace':")
    json_str = json_str.replace("nameAsSlug:", "'nameAsSlug':")
    json_str = json_str.replace("delivery_urls:", "'delivery_urls':")
    json_str = json_str.replace("service_provider:", "'service_provider':")
    json_str = json_str.replace("url:", "'url':")
    json_str = json_str.replace(
        "deliveryNotAvailableTitle:", "'deliveryNotAvailableTitle':"
    )
    json_str = json_str.replace(
        "deliveryNotAvailableBody:", "'deliveryNotAvailableBody':"
    )
    json_str = json_str.replace("'", '"')
    json_str = (
        json_str.replace("\n", "")
        .replace("\t", "")
        .replace("  ", "")
        .replace(",}", "}")
        .replace(",]", "]")
        .strip()
    )

    store_list = json.loads(json_str)

    for store in store_list:

        page_url = search_url + store["slug"] + "/"
        locator_domain = website

        log.info(page_url)

        location_name = store["name"].strip()
        if "Opening Winter" in store["orderingNotAvailableTitle"]:
            continue
        street_address = store["address1"].strip()

        city = store["address2"].split(",")[0].strip()

        state = store["address2"].split(",")[1].strip()
        zip = "<MISSING>"

        country_code = "CA"
        if us.states.lookup(state):
            country_code = "US"

        store_number = store["id"]

        phone = store["phone"]

        location_type = "<MISSING>"

        hours_info = list(
            filter(
                str,
                search_sel.xpath(
                    f'//div[contains(@class,"titles") and .//h2[contains(text(),"{location_name}")]]/following-sibling::div//div[contains(@class,"hours ")]//text()'
                ),
            )
        )

        hours_info = list(filter(str, [x.strip() for x in hours_info]))[-7:]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        hour_list = []
        for idx, day in enumerate(days, 0):
            timing = hours_info[idx]
            hour_list.append(f"{day}: {timing}")

        hours_of_operation = "; ".join(hour_list)
        latitude = store["lat"]
        longitude = store["long"]

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
