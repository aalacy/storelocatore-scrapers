# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fremontbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.fremontbank.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[contains(@class,"location-listings")]/ul/li[position()>1]'
    )
    for store in stores:
        store_json = json.loads("".join(store.xpath("@data-location")).strip())
        page_url = "".join(
            store.xpath('.//a[contains(text(),"Branch Details")]/@href')
        ).strip()
        location_type = "Branch"
        locator_domain = website
        street_address = "<MISSING>"
        state = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        address = ""
        if len(page_url) > 0:
            page_url = "https://www.fremontbank.com" + page_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            sections = store_sel.xpath('//div[@class="media-body"]')
            for section in sections:
                if "BRANCH ADDRESS" in "".join(section.xpath("strong/text()")).strip():
                    address = section.xpath("text()")
                    break

            hours_list = []
            if len(sections) > 0:
                temp_hours = sections[0].xpath("text()")
                for temp in temp_hours:
                    if len("".join(temp).strip()) > 0:
                        hours_list.append("".join(temp).strip())

            hours_of_operation = "; ".join(hours_list).strip()

        location_name = store_json["location"]
        if "ATM Only" in location_name:
            location_type = "ATM Only"

        if len(address) <= 0:
            address = "".join(store.xpath(".//button/@data-address")).strip().split(",")
            street_address = ", ".join(address[:-1]).strip()

            city = store_json["city"].strip()
            street_address = street_address.replace(city, "").strip()
            state = address[-1].strip().split(" ")[0].strip()
            zipp = store_json["zipcode"]
        else:
            add_list = []
            for temp in address:
                if len("".join(temp).strip()) > 0:
                    add_list.append("".join(temp).strip())

            street_address = ", ".join(add_list[:-1]).strip()
            city = add_list[-1].strip().split(",")[0].strip()
            state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
            zipp = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()

            if len(street_address) <= 0:
                street_address = "".join(add_list).strip().split(",")[0].strip()
                city = "".join(add_list).strip().split(",")[1].strip()
                state = (
                    "".join(add_list)
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .split(" ")[0]
                    .strip()
                )
                zipp = (
                    "".join(add_list)
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                    .strip()
                )

        country_code = "US"
        phone = "".join(store.xpath('.//div[@class="open-closed"]/text()')).strip()

        store_number = "<MISSING>"

        latitude = store_json["position"]["lat"]
        longitude = store_json["position"]["lng"]

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
