# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "usc.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.usc.co.uk/stores/all"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="letItems"]')
        for store in stores:

            page_url = (
                "https://www.usc.co.uk"
                + "".join(store.xpath("a/@href")).strip().replace("../", "/").strip()
            )
            log.info(page_url)
            locator_domain = website

            store_req = session.get(page_url, headers=headers)
            if isinstance(store_req, SgRequestError):
                continue

            retry_count = 0
            while "var store =" not in store_req.text and retry_count < 3:
                store_req = session.get(page_url, headers=headers)
                retry_count = retry_count + 1

            store_sel = lxml.html.fromstring(store_req.text)
            if "var store =" in store_req.text:
                store_json = json.loads(
                    store_req.text.split("var store =")[1]
                    .strip()
                    .split("};")[0]
                    .strip()
                    + "}"
                )

                location_name = store_json["formattedStoreNameLong"]
                street_address = (
                    store_json["address"]
                    .replace("\r\n", "")
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
                raw_address = street_address
                city = store_json["town"]
                if city and len(city) > 0:
                    raw_address = raw_address + ", " + city

                state = store_json["county"]
                if state and len(state) > 0:
                    raw_address = raw_address + ", " + state

                zip = store_json["postCode"]
                if zip and len(zip) > 0:
                    raw_address = raw_address + ", " + zip

                country_code = store_json["countryCode"]

                store_number = str(store_json["code"])
                phone = store_json["telephone"]

                location_type = store_json["shortMessage"]

                hours = store_json["openingTimes"]
                hours_list = []
                for hour in hours:
                    if hour["dayOfWeek"] == 0:
                        day = "Monday:"
                    if hour["dayOfWeek"] == 1:
                        day = "Tuesday:"
                    if hour["dayOfWeek"] == 2:
                        day = "Wednesday:"
                    if hour["dayOfWeek"] == 3:
                        day = "Thursday:"
                    if hour["dayOfWeek"] == 4:
                        day = "Friday:"
                    if hour["dayOfWeek"] == 5:
                        day = "Saturday:"
                    if hour["dayOfWeek"] == 6:
                        day = "Sunday:"

                    if (
                        hour["openingTime"] is not None
                        and hour["closingTime"] is not None
                    ):
                        time = hour["openingTime"] + "-" + hour["closingTime"]
                        hours_list.append(day + time)
                    else:
                        time = "Closed"
                        hours_list.append(day + time)

                hours_of_operation = ";".join(hours_list).strip()
                latitude = store_json["latitude"]
                longitude = store_json["longitude"]

                if phone == "N/A":
                    phone = "<MISSING>"

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
            else:
                location_name = "".join(
                    store_sel.xpath('//div[@id="StoreDetailsContainer"]/h1/text()')
                ).strip()
                if len(location_name) <= 0:
                    continue

                raw_address = store_sel.xpath(
                    '//div[@id="StoreDetailsContainer"]//div[@class="StoreFinderList"][./div[@itemprop="address"]]/div/text()'
                )

                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = "<MISSING>"
                zip = raw_address[-1]
                country_code = "".join(store.xpath("@data-country-code")).strip()

                store_number = page_url.split("-")[-1].strip()
                phone = "".join(
                    store_sel.xpath(
                        '//div[@id="StoreDetailsContainer"]//span[@itemprop="telephone"]/text()'
                    )
                ).strip()

                location_type = "<MISSING>"

                hours = store_sel.xpath(
                    '//div[@id="StoreDetailsContainer"]//div[./meta[@itemprop="openingHours"]]/text()'
                )
                hours_list = []
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

                hours_of_operation = ";".join(hours_list).strip()
                latitude = (
                    "".join(
                        store_sel.xpath(
                            '//div[@id="GoogleStaticStoreMapContainer"]/@data-center'
                        )
                    )
                    .strip()
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(
                        store_sel.xpath(
                            '//div[@id="GoogleStaticStoreMapContainer"]/@data-center'
                        )
                    )
                    .strip()
                    .split(",")[-1]
                    .strip()
                )

                if phone == "N/A":
                    phone = "<MISSING>"

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
