# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "eyecarecenter.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.eyecarecenter.com/locations/"
    api_url = "https://www.eyecarecenter.com/_next/data/{}/locations.json"
    with SgRequests(proxy_country="us", dont_retry_status_codes=([404])) as session:
        buildID = (
            session.get("https://www.eyecarecenter.com/locations", headers=headers)
            .text.split('"buildId":"')[1]
            .strip()
            .split('",')[0]
            .strip()
        )
        log.info(buildID)
        api_res = session.get(api_url.format(buildID), headers=headers)
        json_res = json.loads(api_res.text)
        stores = json_res["pageProps"]["locations"]

        for store in stores:

            page_url = search_url + store["slug"]
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = store["name"]
            location_type = "<MISSING>"
            locator_domain = website

            street_address = store["address1"].strip()

            city = store["city"]
            state = store["state"]
            zip = store["zipCode"]

            country_code = "US"

            store_number = store["sysId"]

            phone = store["phoneNumber"]

            hours = list(
                filter(
                    str,
                    store_sel.xpath(
                        '//div[./h2//text()="Hours of Operation:"]/div/div//text()'
                    ),
                )
            )

            hours_of_operation = "; ".join(hours).replace("day; ", "day: ").strip()

            latitude, longitude = store["map"]["lat"], store["map"]["lon"]

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
