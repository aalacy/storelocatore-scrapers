# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "valleylearningcenters.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "valleylearningcenters.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "referer": "https://valleylearningcenters.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://valleylearningcenters.com/wp-json/wpgmza/v1/markers/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    loc_req = session.get(
        "https://valleylearningcenters.com/locations/", headers=headers
    )
    loc_sel = lxml.html.fromstring(loc_req.text)
    loc_list = loc_sel.xpath('//div[contains(@class,"wp-block-column")]')
    loc_dict = {}
    for loc in loc_list:
        link = "".join(loc.xpath(".//h2//a/@href")).strip()
        temp_address = loc.xpath(".//p//text()")
        loc_dict[link] = temp_address

    for store in stores:
        if store["link"] is not None and len(store["link"]) > 0:
            page_url = store["link"]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = store["title"]

            raw_info = loc_dict[page_url]
            raw_list = []
            for raw in raw_info:
                if len("".join(raw).strip()) > 0:
                    raw_list.append("".join(raw).strip())

            street_address = ", ".join(raw_list[:-1])
            city_state_zip = raw_list[-1]
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

            country_code = "US"

            store_number = store["id"]
            desc_sel = lxml.html.fromstring(store["description"])
            phone = "".join(desc_sel.xpath("//p//text()")).strip()
            if "!" in phone:
                phone = phone.split("!")[1].strip()

            location_type = "<MISSING>"

            hours = list(
                filter(
                    str,
                    store_sel.xpath(
                        '//*[contains(text(),"Take a tour of our ")]/..//p//text()'
                    ),
                )
            )
            hours = [x.strip() for x in hours]
            hours_of_operation = "; ".join(hours).strip().replace("; ;", "").strip()
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
