# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from bs4 import BeautifulSoup as BS
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "approvedcashadvance.com"
domain = "https://approvedcashadvance.com"

log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    states_resp = session.get(
        "https://approvedcashadvance.com/locations.php", headers=headers
    )
    states_sel = lxml.html.fromstring(states_resp.text)

    states = states_sel.xpath('//div[@class="col ml-5 mt-2 mr-4"]/p/a')
    for state in states:
        state_url = "".join(state.xpath("@href")).strip()
        stores_resp = session.get(domain + state_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_resp.text)

        stores = stores_sel.xpath('//div[@id="locationSelect"]/div[@class="add_box"]')

        store_lcations = (
            stores_resp.text.split("var locations = ")[1].strip().split("];")[0].strip()
            + "]"
        )

        store_loc_array = []
        if "]," in store_lcations:
            store_loc_array = json.loads(
                "["
                + BS(store_lcations, "html.parser")
                .get_text()
                .rsplit("],", 1)[0]
                .strip()
                .split("[", 1)[1]
                .strip()
                + "]]"
            )

        count = 0
        for store in stores:
            locator_domain = website
            page_url = ""
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zip = ""
            country_code = ""
            store_number = "<MISSING>"
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            hours_of_operation = ""

            page_url = "".join(
                store.xpath('div[@class="get_directions_btn"][1]/a/@href')
            ).strip()

            if "-" in "".join(store.xpath("span/text()")).strip():
                store_number = (
                    "".join(store.xpath("span/text()")).strip().split("-")[1].strip()
                )

            check_url = ""
            try:
                check_url = page_url.split("/locations/")[1]
            except:
                pass
            if len(check_url) > 0:
                log.info(page_url)
                store_resp = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_resp.text)

                locations = store_sel.xpath(
                    '//div[@class="addres_sec"]//div[@class="add_box"]'
                )
                if len(locations) > 0:
                    cool = (
                        store_resp.text.split("var locations = ")[1]
                        .strip()
                        .split("];")[0]
                        .strip()
                        + "]"
                    )

                    if "]," in cool:
                        loc_array = json.loads(
                            "["
                            + BS(cool, "html.parser")
                            .get_text()
                            .rsplit("],", 1)[0]
                            .strip()
                            .split("[", 1)[1]
                            .strip()
                            + "]]"
                        )

                        for index in range(0, len(locations)):
                            phone_to_be_matched = "".join(
                                store.xpath("b/a/text()")
                            ).strip()
                            phone = "".join(
                                locations[index].xpath("b/a/text()")
                            ).strip()

                            if phone_to_be_matched == phone:
                                location_name = "".join(
                                    locations[index].xpath("span/text()")
                                ).strip()
                                if "-" in location_name:
                                    location_name = location_name.split("-")[0].strip()

                                temp_address = locations[index].xpath("text()")
                                add_list = []
                                for addr in temp_address:
                                    if len("".join(addr).strip()) > 0:
                                        add_list.append("".join(addr).strip())

                                street_address = add_list[0].strip()
                                city = add_list[1].split(",")[0].strip()
                                state = add_list[1].split(",")[1].strip()
                                zip = "<MISSING>"
                                country_code = "US"
                                location_type = "<MISSING>"
                                latitude = loc_array[index][1]
                                longitude = loc_array[index][2]
                                hours_of_operation = ""
                                temp_hours = store_sel.xpath(
                                    '//div[@class="hoursoperation_sec"]/text()'
                                )
                                hours_list = []
                                for hour in temp_hours:
                                    if len("".join(hour).strip()) > 0:
                                        hours_list.append("".join(hour).strip())

                                hours_of_operation = " ".join(hours_list).strip()
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
                else:
                    page_url = domain + state_url
                    locator_domain = website
                    location_name = "".join(store.xpath("span/text()")).strip()
                    if "-" in location_name:
                        location_name = location_name.split("-")[0].strip()

                    temp_address = store.xpath("text()")
                    add_list = []
                    for addr in temp_address:
                        if len("".join(addr).strip()) > 0:
                            add_list.append("".join(addr).strip())

                    street_address = add_list[0].strip()
                    city = add_list[1].split(",")[0].strip()
                    state = add_list[1].split(",")[1].strip()
                    zip = "<MISSING>"
                    country_code = "US"
                    phone = "".join(store.xpath("b/a/text()")).strip()
                    location_type = "<MISSING>"
                    latitude = store_loc_array[count][1]
                    longitude = store_loc_array[count][2]
                    hours_of_operation = "<MISSING>"

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
            else:

                page_url = domain + state_url
                locator_domain = website
                location_name = "".join(store.xpath("span/text()")).strip()
                if "-" in location_name:
                    location_name = location_name.split("-")[0].strip()

                temp_address = store.xpath("text()")
                add_list = []
                for addr in temp_address:
                    if len("".join(addr).strip()) > 0:
                        add_list.append("".join(addr).strip())

                street_address = add_list[0].strip()
                city = add_list[1].split(",")[0].strip()
                state = add_list[1].split(",")[1].strip()
                zip = "<MISSING>"
                country_code = "US"
                phone = "".join(store.xpath("b/a/text()")).strip()
                location_type = "<MISSING>"
                latitude = store_loc_array[count][1]
                longitude = store_loc_array[count][2]
                hours_of_operation = "<MISSING>"

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

            count = count + 1


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
