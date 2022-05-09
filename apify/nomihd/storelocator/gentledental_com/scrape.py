# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "gentledental.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.gentledental.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.gentledental.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    data = '{"lat":"42.360406","lng":"-71.057993","miles":0}'

    search_url = "https://www.gentledental.com/location/list/"
    stores_req = session.post(search_url, headers=headers, data=data)
    stores = json.loads(stores_req.text)["gdOffices"]

    for store in stores:

        page_url = (
            "https://www.gentledental.com"
            + store["link"].replace("#sst-FormWrapper", "").strip()
        )
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = store["title"]
        location_type = "<MISSING>"
        locator_domain = website

        street_address = store["address"]
        city_state_zip = store["cityStateZip"]
        city = city_state_zip.strip().split(",")[0].strip()
        state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        phone = store["phone"]

        hours_list = []
        hours = store_sel.xpath('//div[@class="office-hours"]')
        if len(hours) > 0:
            hours = hours[0].xpath('div[@class="office-hours__item"]')
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                time = "".join(hour.xpath("span[2]/text()")).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["geoLocation"]["lat"]
        longitude = store["geoLocation"]["lng"]

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
