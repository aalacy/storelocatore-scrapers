# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "tedi.de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "liveapi.yext.com",
    "accept": "*/*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "origin": "https://stores.tedi.com",
    "referer": "https://stores.tedi.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:

        countries_req = session.get(
            "https://www.tedi.com/filialfinder/", headers=headers
        )
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath('//ul[@id="languageMenu"]/li/a')
        for country in countries:
            country_name = "".join(country.xpath(".//span/text()")).strip()
            log.info(country_name)
            api_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location={}&offset={}&limit=50&api_key=c021846c72fa8bb9ff555d4b1a6eaadf&v=20181201&resolvePlaceholders=true&languages=en&entityTypes=location"
            offset = 0
            while True:
                final_url = api_url.format(country_name, str(offset))

                api_res = session.get(final_url, headers=headers)

                json_res = json.loads(api_res.text)

                store_list = json_res["response"]["entities"]

                if not store_list:
                    break

                for store in store_list:

                    store_number = store["meta"]["id"]
                    page_url = store.get("landingPageUrl", "")

                    locator_domain = website

                    location_name = (
                        store["c_storeName"]
                        if "c_storeName" in store
                        else store["name"]
                    )
                    if "coming soon" in location_name.lower():
                        continue
                    street_address = store["address"]["line1"].strip()
                    if "line2" in store and store["address"]:
                        street_address = (
                            street_address + ", " + store["address"]["line2"]
                        ).strip(", .")

                    city = store["address"].get("city", "<MISSING>").strip()
                    state = store["address"].get("region", "<MISSING>").strip()

                    zip = store["address"].get("postalCode", "<MISSING>").strip()

                    country_code = store["address"]["countryCode"].strip()
                    phone = store.get("mainPhone", "<MISSING>")

                    location_type = "<MISSING>"
                    hours = store.get("hours", "")
                    hour_list = []
                    if hours:
                        for day in [
                            "monday",
                            "tuesday",
                            "wednesday",
                            "thursday",
                            "friday",
                            "saturday",
                            "sunday",
                        ]:
                            if hours[day].get("openIntervals"):
                                hour_list.append(
                                    f"{day}: {hours[day]['openIntervals'][0]['start']} - {hours[day]['openIntervals'][0]['end']}"
                                )
                            else:
                                hour_list.append(f"{day}: Closed")

                    hours_of_operation = "; ".join(hour_list)

                    latitude = store["yextDisplayCoordinate"]["latitude"]
                    longitude = store["yextDisplayCoordinate"]["longitude"]

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

                offset = offset + 50


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
