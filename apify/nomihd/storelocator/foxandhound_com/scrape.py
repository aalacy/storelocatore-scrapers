# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "foxandhound.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.foxandhound.com/locations/index"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="locationLink"]/@href')
    for store_url in stores:
        page_url = "https://www.foxandhound.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locID = (
            store_req.text.split('"locId":')[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        API_URL = "https://api.momentfeed.com/v1/lf/location/store-info/{}".format(
            locID
        )
        log.info(API_URL)
        api_req = session.get(API_URL)
        locator_domain = website
        if not isinstance(api_req, SgRequestError):
            store_json = json.loads(api_req.text)
            location_name = store_json["name"]

            street_address = store_json["address"]
            if (
                store_json["addressExtended"] is not None
                and len(store_json["addressExtended"]) > 0
            ):
                street_address = street_address + ", " + store_json["addressExtended"]

            city = store_json["locality"]
            state = store_json["region"]
            zip = store_json["postcode"]
            country_code = store_json["country"]

            phone = store_json["phone"]
            location_type = store_json["status"]
            store_number = locID

            hours_list = []
            if location_type == "open":
                hours = store_json["hours"].split(";")
                for index in range(0, len(hours) - 1):
                    day_val = hours[index].split(",")[0].strip()
                    if day_val == "1":
                        day = "Monday:"
                    if day_val == "2":
                        day = "Tuesday:"
                    if day_val == "3":
                        day = "Wednesday:"
                    if day_val == "4":
                        day = "Thursday:"
                    if day_val == "5":
                        day = "Friday:"
                    if day_val == "6":
                        day = "Saturday:"
                    if day_val == "7":
                        day = "Sunday:"

                    hours_list.append(
                        day + hours[index].split(",", 1)[1].replace(",", " - ").strip()
                    )

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

        else:
            location_name = "".join(
                store_sel.xpath(
                    '//h3[@class="text-center locations-address-head"]/text()'
                )
            ).strip()

            raw_address = store_sel.xpath(
                '//div[@class="row no-gutters locations-address justify-content-center"]//p/text()'
            )
            street_address = raw_address[0].strip()
            city = raw_address[-1].strip().split(" ")[0].strip()
            state = raw_address[-1].strip().split(" ")[1].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]/text()')
            ).strip()
            location_type = "<MISSING>"
            store_number = locID

            hours_of_operation = "<MISSING>"
            map_link = "".join(
                store_sel.xpath('//a[@class="text-center locationLink"]/@href')
            ).strip()
            latitude = (
                map_link.split("/")[-1]
                .strip()
                .split(",")[0]
                .strip()
                .replace("+", "")
                .strip()
            )
            longitude = map_link.split("/")[-1].strip().split(",")[-1].strip()

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
