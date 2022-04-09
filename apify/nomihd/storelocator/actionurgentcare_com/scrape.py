# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "actionurgentcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "actionurgentcare.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://actionurgentcare.com"

    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[./div/div/b/text()="Locations"]//li/a')
    build_id = search_res.text.split('"buildId":')[1].split(",")[0].strip('" ')

    for store in store_list:

        broken_link = "".join(store.xpath("./@href"))

        page_url = broken_link
        if "https" not in page_url:
            page_url = search_url + page_url

        store_api_url = f"{search_url}/_next/data/{build_id}/en-US{broken_link}.json"
        store_res = session.get(store_api_url, headers=headers)

        store_info = (json.loads(store_res.text))["pageProps"]["clinic"]

        locator_domain = website

        if store_info.get("address"):

            street_address = store_info["address"]["street"]
            city = store_info["address"]["city"]
            state = store_info["address"]["state"]
            zip = store_info["address"]["zipCode"]
            country_code = "US"
        else:
            street_address, city, state, zip = (
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            )

        location_name = store_info["title"]

        phone = store_info["phoneNumber"]

        store_number = store_info["appointment"]["officeId"]

        location_type = "<MISSING>"
        if store_info.get("telemedicineOnly"):
            continue
        hours_of_operation = store_info["businessHoursShort"]

        if store_info.get("map"):
            latitude, longitude = (
                store_info["map"]["coords"]["lat"],
                store_info["map"]["coords"]["lng"],
            )
        else:
            latitude, longitude = "<MISSING>", "<MISSING>"
        raw_address = "<MISSING>"

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
