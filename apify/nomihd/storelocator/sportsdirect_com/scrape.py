# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "sportsdirect.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.sportsdirect.com/stores/all"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="letItems"]')
        for store in stores:
            page_url = (
                "https://www.sportsdirect.com"
                + "".join(store.xpath("a/@href")).strip().replace("../", "/").strip()
            )
            log.info(page_url)
            locator_domain = website

            try:
                store_req = SgRequests.raise_on_err(
                    session.get(page_url, headers=headers)
                )
            except SgRequestError as e:
                log.info(e.status_code)

            retry_count = 0
            while "var store =" not in store_req.text and retry_count < 3:
                try:
                    store_req = SgRequests.raise_on_err(
                        session.get(page_url, headers=headers)
                    )
                    retry_count = retry_count + 1
                except SgRequestError as e:
                    log.info(e.status_code)

            if store_req:
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
                    street_address = store_json["address"]
                    city = store_json["town"]
                    if city == "Festival Place Shopping Centre":
                        city = "Basingstoke"

                    state = store_json["county"]
                    zip = store_json["postCode"]
                    raw_address = ""
                    if street_address and len(street_address) > 0:
                        raw_address = street_address
                    if city and len(city) > 0:
                        raw_address = raw_address + ", " + city
                    if state and len(state) > 0:
                        raw_address = raw_address + ", " + state
                    if zip and len(zip) > 0:
                        raw_address = raw_address + ", " + zip

                    country_code = store_json["countryCode"]
                    if country_code != "GB" and country_code != "IE":
                        state = "<MISSING>"

                    store_number = str(store_json["code"])
                    phone = store_json["telephone"]

                    location_type = store_json["storeType"]

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

                    hours_of_operation = ";".join(hours_list).strip()
                    latitude = store_json["latitude"]
                    longitude = store_json["longitude"]
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

                    temp_address = store_sel.xpath(
                        '//div[@id="StoreDetailsContainer"]//div[@class="StoreFinderList"][./div[@itemprop="address"]]/div/text()'
                    )

                    add_list = []
                    raw_address = ""
                    for temp in temp_address:
                        if len("".join(temp).strip()) > 0:
                            add_list.append("".join(temp).strip())

                    raw_address = ", ".join(add_list).strip()
                    street_address = temp_address[0].strip()
                    city = temp_address[1].strip()
                    state = "<MISSING>"
                    zip = temp_address[-1]
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
