# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "bahamabreeze.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here
    headers = {
        "authority": "www.bahamabreeze.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.bahamabreeze.com/locations/all-locations",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    search_url = "https://www.bahamabreeze.com/locations/all-locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="cal_col"]/ul//li/a/@href')
    for store_url in stores:
        page_url = "https://www.bahamabreeze.com" + store_url.strip()
        locator_domain = website
        log.info(page_url)
        headers = {
            "authority": "www.bahamabreeze.com",
            "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            "sec-ch-ua-mobile": "?0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://www.bahamabreeze.com/locations/all-locations",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        }

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        for js in json_list:
            if "@type" in js:
                if json.loads(js)["@type"] == "Restaurant":
                    json_text = js
                    store_json = json.loads(json_text)
                    hours_of_operation = ""
                    hours_list = []
                    hours = store_json["openingHours"]
                    for hour in hours:
                        if len("".join(hour).strip()) > 0:
                            hours_list.append("".join(hour).strip())

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude = store_json["geo"]["latitude"]
                    longitude = store_json["geo"]["longitude"]

        location_name = "".join(
            store_sel.xpath('//h1[@class="style_h1"]/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = "".join(
            store_sel.xpath('//p[@id="info-link-webhead"]/text()[1]')
        ).strip()
        city_state_Zip = "".join(
            store_sel.xpath('//p[@id="info-link-webhead"]/text()[2]')
        ).strip()
        city = city_state_Zip.split(",")[0].strip()
        state = city_state_Zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_Zip.split(",")[1].strip().split(" ")[1].strip()
        country_code = "US"

        store_number = page_url.split("/")[-1].strip()
        if store_number.isdigit() is False:
            store_number = "<MISSING>"

        phone = "".join(
            store_sel.xpath('//p[@id="info-link-webhead"]/text()[3]')
        ).strip()

        location_type = "<MISSING>"

        if len(hours_of_operation) <= 0:
            hours_list = []
            hours = store_sel.xpath('//div[@class="hours-section"]/span')
            total = int((len(hours) / 2))
            for index in range(0, total):
                hours_list.append(
                    "".join(hours[index].xpath("text()")).strip()
                    + ":"
                    + "".join(hours[index + 1].xpath("text()")).strip()
                )

            hours_of_operation = "; ".join(hours_list).strip()

        if len(hours_of_operation) <= 0:
            hours_list = []
            hours = store_sel.xpath('//div[contains(@class,"week-schedule")]/div')
            for hour in hours:
                day = "".join(hour.xpath("ul/li[1]/text()")).strip()
                if "(" in day:
                    day = day.split("(")[1].strip().replace(")", "").strip()
                time = "".join(hour.xpath("ul/li[2]//text()")).strip()
                hours_list.append(day + ":" + time)
            hours_of_operation = "; ".join(hours_list).strip()

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
