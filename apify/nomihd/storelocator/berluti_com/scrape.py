# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "berluti.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "store.berluti.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://store.berluti.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://store.berluti.com/"
    with SgRequests() as session:
        home_req = session.get(search_url, headers=headers)
        home_sel = lxml.html.fromstring(home_req.text)
        countries = home_sel.xpath('//select[@id="country-input"]/option/@value')
        for country in countries:
            params = {
                "countries[]": country,
                "query": "",
                "lat": "",
                "lon": "",
                "geo": "0",
            }

            stores_req = session.get(
                "https://store.berluti.com/search",
                params=params,
                headers=headers,
            )
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = list(
                set(stores_sel.xpath('//a[contains(text(),"Go to store")]/@href'))
            )
            for store_url in stores:
                page_url = "https://store.berluti.com" + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                for js in json_list:
                    if json.loads(js, strict=False)["@type"] == "LocalBusiness":
                        store_json = json.loads(js, strict=False)
                        locator_domain = website

                        store_number = "<MISSING>"

                        location_type = "<MISSING>"
                        location_name = store_json["name"]

                        street_address = store_json["address"]["streetAddress"]
                        city = store_json["address"]["addressLocality"]
                        state = "<MISSING>"
                        zip = store_json["address"]["postalCode"]

                        country_code = store_json["address"]["addressCountry"]

                        phone = store_json["telephone"].replace("+1", "").strip()

                        hours = store_sel.xpath(
                            '//div[@id="lf-parts-opening-hours-content"]/div'
                        )
                        hours_list = []
                        for hour in hours:
                            day = "".join(hour.xpath("span/text()")).strip()
                            raw_time = (
                                "".join(hour.xpath("div//text()"))
                                .strip()
                                .replace("\n", "")
                                .strip()
                            )
                            if "-" in raw_time:
                                time = (
                                    raw_time.split("-")[0].strip()
                                    + "-"
                                    + raw_time.split("-")[1].strip()
                                )
                            else:
                                time = raw_time
                            hours_list.append(day + ":" + time)

                        hours_of_operation = (
                            "; ".join(hours_list)
                            .strip()
                            .replace("\n", "")
                            .strip()
                            .replace("Today opening hours", "")
                            .strip()
                        )

                        latitude, longitude = (
                            store_json["geo"]["latitude"],
                            store_json["geo"]["longitude"],
                        )

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


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
