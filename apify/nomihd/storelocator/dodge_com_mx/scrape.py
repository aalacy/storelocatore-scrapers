# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dodge.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.dodge.com.mx/distribuidores"

    with SgRequests(dont_retry_status_codes=([404]), verify_ssl=False) as session:
        search_res = session.get(api_url, headers=headers)
        json_str = (
            search_res.text.split("data-items=")[1]
            .split("data-dealers-")[0]
            .strip("' ")
            .strip()
        )
        json_res = json.loads(json_str)
        for node in json_res.keys():
            stores = json_res[node]["items"]

            if isinstance(stores, list):
                for store in stores:

                    locator_domain = website

                    location_name = store["name"]
                    page_url = store["url"]

                    location_type = "<MISSING>"

                    raw_address = store["address"]
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    if street_address is not None:
                        street_address = street_address.replace("Ste", "Suite")
                    city = formatted_addr.city
                    state = "<MISSING>"

                    zip = formatted_addr.postcode
                    if zip:
                        zip = zip.replace("C.P.", "").strip()

                    country_code = "MX"

                    phone = store["tel"]
                    if phone:
                        phone = phone[0]

                    hours_of_operation = "<MISSING>"

                    try:
                        if page_url:
                            log.info(page_url)
                            store_res = SgRequests.raise_on_err(
                                session.get(page_url, headers=headers)
                            )
                            try:
                                store_sel = lxml.html.fromstring(store_res.text)

                                hours = list(
                                    filter(
                                        str,
                                        [
                                            x.strip()
                                            for x in store_sel.xpath(
                                                '//h6[contains(text(),"Horario de Ventas")]/../ul/li//text()'
                                            )
                                        ],
                                    )
                                )
                                if len(hours) <= 0:
                                    hours = list(
                                        filter(
                                            str,
                                            [
                                                x.strip()
                                                for x in store_sel.xpath(
                                                    '//div[./strong[contains(text(),"Horario de Ventas")]]/text()'
                                                )
                                            ],
                                        )
                                    )
                                hours_of_operation = (
                                    "; ".join(hours).replace(".;", ":").strip()
                                )
                                if "Por favor contacta al" in hours_of_operation:
                                    hours_of_operation = "<MISSING>"

                            except:
                                pass
                    except SgRequestError as e:
                        log.error(e.status_code)

                    store_number = store["id"]

                    latitude, longitude = store["lat"], store["long"]

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
            elif isinstance(stores, dict):
                for key in stores.keys():
                    store = stores[key]
                    locator_domain = website

                    location_name = store["name"]
                    page_url = store["url"]

                    location_type = "<MISSING>"

                    raw_address = store["address"]
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    if street_address is not None:
                        street_address = street_address.replace("Ste", "Suite")
                    city = formatted_addr.city
                    state = formatted_addr.state

                    zip = formatted_addr.postcode

                    country_code = "MX"

                    phone = store["tel"]
                    if phone:
                        phone = phone[0]

                    hours_of_operation = "<MISSING>"

                    try:
                        if page_url:
                            log.info(page_url)
                            store_res = SgRequests.raise_on_err(
                                session.get(page_url, headers=headers)
                            )
                            store_sel = lxml.html.fromstring(store_res.text)

                            hours = list(
                                filter(
                                    str,
                                    [
                                        x.strip()
                                        for x in store_sel.xpath(
                                            '//h6[contains(text(),"Horario de Ventas")]/../ul/li//text()'
                                        )
                                    ],
                                )
                            )
                            if len(hours) <= 0:
                                hours = list(
                                    filter(
                                        str,
                                        [
                                            x.strip()
                                            for x in store_sel.xpath(
                                                '//div[./strong[contains(text(),"Horario de Ventas")]]/text()'
                                            )
                                        ],
                                    )
                                )

                            hours_of_operation = (
                                "; ".join(hours).replace(".;", ":").strip()
                            )
                            if "Por favor contacta al" in hours_of_operation:
                                hours_of_operation = "<MISSING>"

                    except SgRequestError as e:
                        log.error(e.status_code)

                    store_number = store["id"]

                    latitude, longitude = store["lat"], store["long"]

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
