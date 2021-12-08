# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser
import json

website = "jeep-caribbean.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.jeep-caribbean.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jeep-caribbean.com/shopping-tools/find-a-dealer.html"
    with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
        search_res = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(search_res.text)
        stores_sel = lxml.html.fromstring(
            json.loads(
                "".join(
                    stores_sel.xpath(
                        '//div[@data-component="StandAloneTextContainer"]/@data-props'
                    )
                )
                .strip()
                .replace("&#34;", '"')
                .replace("&lt;", "<")
                .replace("&#39;", "'")
                .strip()
            )["contentModules"][0]["components"][0]["content"]["text"]
        )
        stores = stores_sel.xpath('//p[./a[contains(text(),"View Website:")]]')
        for store in stores:
            location_type = "<MISSING>"
            page_url = search_url
            locator_domain = website
            temp_loc = store.xpath("b/text()")
            loc_list = []
            for loc in temp_loc:
                if len("".join(loc).strip()) > 0:
                    loc_list.append("".join(loc).strip())

            store_info = store.xpath("text()")
            if len(loc_list) > 1:
                add_index = 0
                ph_index = 1
                for index in range(0, len(loc_list)):
                    location_name = loc_list[0]
                    raw_address = store_info[add_index]
                    add_index = add_index + 2
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if street_address:
                        if formatted_addr.street_address_2:
                            street_address = (
                                street_address + ", " + formatted_addr.street_address_2
                            )
                    else:
                        if formatted_addr.street_address_2:
                            street_address = formatted_addr.street_address_2

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    country_code = raw_address.split(",")[-1].strip()
                    if country_code == "VG1110":
                        country_code = "BRITISH VIRGIN ISLANDS"

                    phone = (
                        "".join(store_info[ph_index])
                        .strip()
                        .replace("Phone:", "")
                        .strip()
                    )
                    ph_index = ph_index + 2
                    store_number = "<MISSING>"

                    hours_of_operation = "<MISSING>"
                    latitude, longitude = "<MISSING>", "<MISSING>"
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
                location_name = "".join(loc_list).strip()
                raw_address = store_info[0]

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address:
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                else:
                    if formatted_addr.street_address_2:
                        street_address = formatted_addr.street_address_2

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = raw_address.split(",")[-1].strip()
                if country_code == "VG1110":
                    country_code = "BRITISH VIRGIN ISLANDS"

                phone = "".join(store_info[1]).strip().replace("Phone:", "").strip()
                store_number = "<MISSING>"

                hours_of_operation = "<MISSING>"
                latitude, longitude = "<MISSING>", "<MISSING>"
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
