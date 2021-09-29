# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.co.in"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "restaurants.pizzahut.co.in",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://restaurants.pizzahut.co.in/?page={}"
    page_no = 1
    with SgRequests(
        verify_ssl=False, proxy_country="in", dont_retry_status_codes=([404])
    ) as session:
        while True:
            search_res = session.get(search_url.format(str(page_no)), headers=headers)

            stores_sel = lxml.html.fromstring(search_res.text)
            stores = stores_sel.xpath(
                '//a[@class="btn btn-website"][./span[contains(text(),"Details")]]/@href'
            )
            for store_url in stores:
                page_url = store_url
                locator_domain = website
                if (
                    page_url
                    == "https://restaurants.pizzahut.co.in/pizza-hut-ph-padmini-mall-chittorgarh-pizza-restaurant-gandhi-nagar-sector-3-chittorgarh-122098/Home"
                ):
                    continue
                log.info(page_url)
                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)
                json_list = json.loads(
                    "".join(
                        store_sel.xpath('//script[@type="application/ld+json"]/text()')
                    ).strip()
                )
                for js in json_list:
                    if js["@type"] == "Restaurant":
                        store_json = js

                        locator_domain = website
                        location_name = "Pizza Hut"
                        if "alternateName" in store_json:
                            location_name = store_json["alternateName"]
                        street_address = store_json["address"]["streetAddress"]
                        city = store_json["address"]["addressLocality"]
                        state = store_json["address"]["addressRegion"]
                        zip = store_json["address"]["postalCode"]

                        country_code = store_json["address"]["addressCountry"]

                        store_number = "<MISSING>"
                        phone = store_json["telephone"]
                        if len(phone) > 0:
                            phone = phone[0]

                        location_type = "<MISSING>"
                        hours = store_json["openingHoursSpecification"]
                        hours_list = []
                        for hour in hours:
                            day = hour["dayOfWeek"]
                            time = hour["opens"] + "-" + hour["closes"]
                            hours_list.append(day + ": " + time)

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
                        break

            next_page = stores_sel.xpath('//li[@class="next"]/a/@href')
            if len(next_page) > 0:
                page_no = page_no + 1
            else:
                break


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
