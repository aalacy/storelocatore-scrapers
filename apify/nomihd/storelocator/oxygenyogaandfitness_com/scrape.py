# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgpostal import sgpostal as parser
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "oxygenyogaandfitness.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://oxygenyogaandfitness.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://oxygenyogaandfitness.com/oxygen-yoga-locations/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://oxygenyogaandfitness.com/wp-admin/admin-ajax.php"

    data = {
        "store_locatore_search_input": "Vancouver, BC, Canada",
        "store_locatore_search_radius": "50000",
        "store_locator_category": "",
        "action": "make_search_request_custom_maps",
        "map_id": "38475",
        "lat": "49.2827291",
        "lng": "-123.1207375",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(
        stores_req.text.split("var locations = ")[1].strip().split("}]};")[0].strip()
        + "}]}"
    )["locations"]
    for store in stores:
        store_sel = lxml.html.fromstring(store["infowindow"])
        page_url = "".join(
            store_sel.xpath('//div[@class="store-infowindow"]/div/span/a/@href')
        ).strip()
        location_name = "".join(
            store_sel.xpath('//div[@class="store-infowindow"]/div/h3/text()')
        ).strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        if stores_req.ok is True:
            store_page_sel = lxml.html.fromstring(store_req.text)
            add_list = []
            temp_add = store_page_sel.xpath(
                '//div[@class="et_pb_text_inner"][./h1[contains(text(),"LOCATED AT") or contains(text(),"located at") or contains(text(),"Located at") or contains(text(),"Located At")]]/p//text()'
            )
            if len(temp_add) <= 0:
                temp_add = store_page_sel.xpath(
                    '//div[@class="et_pb_text_inner"][.//h1[contains(text(),"LOCATED AT") or contains(text(),"located at") or contains(text(),"Located at") or contains(text(),"Located At")]]/div/div/div//text()'
                )

            if len(temp_add) <= 0:
                temp_add = store_page_sel.xpath(
                    '//div[@class="et_pb_text_inner"][.//h1[contains(text(),"LOCATED AT") or contains(text(),"located at") or contains(text(),"Located at") or contains(text(),"Located At")]]/div/div/p/text()'
                )
            if len(temp_add) <= 0:
                temp_add = store_page_sel.xpath(
                    '//div[@class="et_pb_text_inner"][./h2[contains(text(),"LOCATED AT") or contains(text(),"located at") or contains(text(),"Located at") or contains(text(),"Located At")]]/p//text()'
                )
            if len(temp_add) <= 0:
                temp_add = store_page_sel.xpath(
                    f'//div[@class="et_pb_text_inner"][.//h1[contains(text(),"{location_name}")]]/div/div/div/text()'
                )

            if len(temp_add) > 0:
                for phn_idx, x in enumerate(temp_add):
                    if bool(re.search("^[0-9-.() ]{1,17}$", x)):
                        break
                if re.search("^[0-9-.() ]{1,17}$", temp_add[phn_idx]):
                    full_address = temp_add[:phn_idx]
                    for add in full_address:
                        if (
                            len("".join(add).strip()) > 0
                            and "(Yoga)" not in "".join(add).strip()
                            and "@" not in "".join(add).strip()
                        ):
                            add_list.append("".join(add).strip())
                else:
                    full_address = temp_add
                    for add in full_address:
                        if (
                            len("".join(add).strip()) > 0
                            and "(Yoga)" not in "".join(add).strip()
                            and "@" not in "".join(add).strip()
                        ):
                            add_list.append("".join(add).strip())

        locator_domain = website

        raw_address = ""
        if len(add_list) > 0:
            raw_address = ", ".join(add_list).strip()
        else:
            raw_address = "".join(
                store_sel.xpath('//div[@class="store-infowindow"]/div/p[2]/text()')
            ).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = "".join(
            store_sel.xpath('//div[@class="store-infowindow"]/div/span/p//text()')
        ).strip()
        hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

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
