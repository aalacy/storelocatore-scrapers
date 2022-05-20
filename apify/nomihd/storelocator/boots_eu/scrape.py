# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "boots.eu"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.boots.eu",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.boots.eu",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.boots.eu/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    stores_req = session.get("https://www.bootsapotheek.nl/stores", headers=headers)
    jsonLocations = json.loads(
        stores_req.text.split("jsonLocations: ")[1]
        .strip()
        .split("imageLocations")[0]
        .strip()[:-1]
    )
    stores = jsonLocations["items"]
    htmlLocations = lxml.html.fromstring(jsonLocations["block"])
    html_stores = htmlLocations.xpath('//div[@class="amlocator-store"]')
    for index, store in enumerate(stores):
        popup_sel = lxml.html.fromstring(store["popup_html"])
        page_url = "".join(
            popup_sel.xpath("//a[@class='amlocator-link']/@href")
        ).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(
            store_sel.xpath("//h1[@class='page-title']//text()")
        ).strip()

        raw_address = "".join(
            store_sel.xpath("//div[@class='amlocator-block']//address/text()")
        ).strip()
        add_list = raw_address.split(",")
        street_address = "".join(add_list[0]).strip()
        city = "".join(add_list[-1]).strip().split(" ", 2)[-1].strip()
        state = "<MISSING>"
        zip = " ".join("".join(add_list[-1]).strip().split(" ")[:2]).strip()
        country_code = "NL"

        phone = "".join(
            store_sel.xpath('//a[@class="amlocator-link icon-phone"]//text()')
        ).strip()

        hours_list = []
        hours = store_sel.xpath('//div[@class="amlocator-schedule-table"]/div')
        for hour in hours:
            day = "".join(hour.xpath("span[1]/text()")).strip()
            time = "".join(hour.xpath("span[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        if hours_of_operation:
            if hours_of_operation.count("Gesloten") == 7:
                continue
        store_number = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

        if len(location_name) <= 0:
            location_name = "".join(
                html_stores[index].xpath('.//div[@class="amlocator-title"]//text()')
            ).strip()

        if len(raw_address) <= 0:
            raw_address = "".join(html_stores[index].xpath(".//address/text()")).strip()
            add_list = raw_address.split(" ")
            street_address = " ".join(add_list[:2]).strip()
            city = "".join(add_list[-1]).strip()
            state = "<MISSING>"
            zip = " ".join(add_list[2:4]).strip()

        if len(phone) <= 0:
            phone = "".join(
                html_stores[index].xpath('.//a[@class="phone"]/text()')
            ).strip()

        if len(hours_list) <= 0:
            hours = html_stores[index].xpath('.//span[@class="store-hours"]/span')

            hours_list = []
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for day_index, hour in enumerate(hours):
                day = days[day_index]
                time = "".join(hour.xpath("text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if hours_of_operation:
                if hours_of_operation.count("Gesloten") == 7:
                    continue

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
