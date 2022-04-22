# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut.fr",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.fr/huts/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//a[@class="mb-10 w-full md:w-1/2 text-left pl-15 py-10 typo-l5"]/@href'
    )

    for store_url in store_list:

        page_url = "https://www.pizzahut.fr" + store_url
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)
        store_json = json.loads(
            "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()
        )

        locator_domain = website
        location_name = store_json["name"]

        street_address = store_json["address"]["streetAddress"]
        city = store_json["address"]["addressLocality"]
        if "Arrondissement" in city:
            city = city.split(" ")[0].strip()

        state = store_json["address"]["addressRegion"]
        zip = store_json["address"]["postalCode"]

        country_code = "FR"

        phone = store_json["telephone"]
        store_number = store_json["branchCode"]
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        hours_list = []
        try:
            temp_dict = {}
            hours = store_json["openingHours"]
            for hour in hours:
                day = hour.split(" ", 1)[0].strip()
                time = ""
                if day in temp_dict:
                    time = (
                        temp_dict[day].split("-")[0].strip()
                        + " - "
                        + hour.split("-")[-1].strip()
                    )
                    temp_dict[day] = time
                else:
                    temp_dict[day] = hour.split(" ", 1)[-1].strip()
                    time = hour.split(" ", 1)[-1].strip()

            for dy in temp_dict.keys():
                hours_list.append(dy + ": " + temp_dict[dy])

        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store_json["geo"]["latitude"]
        longitude = store_json["geo"]["longitude"]

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
