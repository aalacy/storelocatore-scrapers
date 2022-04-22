# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "boots.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def get_page(page_url):
    return session.get(page_url, headers=headers)


def fetch_data():
    search_url = "https://www.boots.ie/store-a-z"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="brand_list_viewer"]//ul/li/a/@href')

    x = 0
    for store_url in stores:
        x = x + 1
        loc_info = parallel_run(store_url)
        if loc_info:
            yield loc_info


def parallel_run(store_url):
    page_url = "https://www.boots.ie" + store_url
    log.info(page_url)
    locator_domain = website

    store_req = get_page(page_url)
    if not isinstance(store_req, SgRequestError):

        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(
            store_sel.xpath('//h2[@class="store_name"]/text()')
        ).strip()
        if location_name == "":
            return None
        sections = store_sel.xpath('//dl[@class="store_info_list"]')
        for sec in sections:
            if (
                "Address"
                in "".join(
                    sec.xpath('dt[@class="store_info_list_label"]/text()')
                ).strip()
            ):

                street_address = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][1]/text()')
                ).strip()
                city = (
                    "".join(sec.xpath('dd[@class="store_info_list_item"][2]/text()'))
                    .strip()
                    .replace("Co.", "")
                    .strip()
                    .replace("Co,", "")
                    .strip()
                )
                if "Dublin" in city:
                    city = "Dublin"

                state = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][3]/text()')
                ).strip()
                zip = "".join(
                    sec.xpath('dd[@class="store_info_list_item"][4]/text()')
                ).strip()
            break

        country_code = "".join(
            store_sel.xpath('//input[@id="storeCountryCode"]/@value')
        ).strip()

        store_number = "".join(
            store_sel.xpath('//input[@name="bootsStoreId"]/@value')
        ).strip()

        phone = "".join(
            store_sel.xpath('//a[@name="Store telephone number"]/text()')
        ).strip()

        location_type = "<MISSING>"
        temp_hours = store_sel.xpath('//table[@class="store_opening_hours "]')
        hours_of_operation = ""
        hours_list = []
        for temp in temp_hours:
            if (
                "Store:"
                in "".join(
                    temp.xpath('thead/tr/th[@class="store_hours_heading"]/text()')
                ).strip()
            ):
                hours = temp.xpath("tbody/tr")
                for hour in hours:
                    day = "".join(
                        hour.xpath('td[@class="store_hours_day"]/text()')
                    ).strip()
                    time = "".join(
                        hour.xpath('td[@class="store_hours_time"]/text()')
                    ).strip()
                    hours_list.append(day + ":" + time)
                break

        hours_of_operation = ";".join(hours_list).strip()

        latitude = "".join(store_sel.xpath('//input[@id="lat"]/@value')).strip()
        longitude = "".join(store_sel.xpath('//input[@id="lon"]/@value')).strip()

        if store_number != "":
            return SgRecord(
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
