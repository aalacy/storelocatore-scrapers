# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "apotek.boots.no"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "zpin.it",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    stores_req = session.get(
        "https://zpin.it/on/location/map/boots/ajax/search.php?&c[z%3Acat%3AALL]=1&c[z%3Acat%3AF%C3%B8flekkskanning]=1&c[z%3Acat%3AMultidose]=1&c[z%3Acat%3AInnhalasjonsveil]=1&c[z%3Acat%3ABlodtrykk]=1&q=&lang=no&mo=440558&mn=default&json",
        headers=headers,
    )
    relations = json.loads(stores_req.text)["relations"]
    for key in relations.keys():
        stores = relations[key]
        for store in stores:
            store_number = store["pin"]["id"]
            location_name = store["pin"]["name"]
            page_url = "https://apotek.boots.no/{}/{}".format(
                location_name.replace(" ", "+").strip(), str(store_number)
            )

            API_URL = "https://zpin.it/on/location/map/boots/ajax/company.php?id={}&lang=no&mo=440558&mn=default&path=".format(
                str(store_number)
            )

            log.info(page_url)
            store_req = session.get(API_URL, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_type = "<MISSING>"
            locator_domain = website

            raw_address = "".join(
                store_sel.xpath("//div[@class='Zaddress']/text()")
            ).strip()
            add_list = raw_address.split(",")
            street_address = "".join(add_list[0]).strip()
            city = "".join(add_list[-1]).strip().split(" ", 1)[-1].strip()
            state = "<MISSING>"
            zip = "".join(add_list[-1]).strip().split(" ", 1)[0]
            country_code = "NO"

            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]/text()')
            ).strip()

            hours_list = []
            hours = store_sel.xpath('//table[@class="openingHours"]//tr')
            for hour in hours:
                day = "".join(hour.xpath("th/text()")).strip()
                time = "".join(hour.xpath("td/text()")).strip()
                if len(time) > 0:
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["pin"]["latlng"]["lat"]
            longitude = store["pin"]["latlng"]["lng"]

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
