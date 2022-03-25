# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "lepainquotidien.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_urls = [
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=United%20States&countryBias=us&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22us%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Argentina&countryBias=ar&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22ar%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Belgium&countryBias=be&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22be%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Brazil&countryBias=br&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22br%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Colombia&countryBias=co&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22co%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=France&countryBias=fr&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22fr%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Netherlands&countryBias=nl&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22nl%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Hong%20Kong&countryBias=hk&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22hk%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Japan&countryBias=jp&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22jp%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Mexico&countryBias=mx&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22mx%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Spain&countryBias=es&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22es%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Switzerland&countryBias=ch&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22ch%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=Turkey&countryBias=tr&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22tr%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=United%20Arab%20Emirates&countryBias=ae&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22ae%22]}}",
        "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=United%20Kingdom&countryBias=gb&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22gb%22]}}",
    ]
    for search_url in search_urls:
        country_code = search_url.split("countryBias=")[1].strip().split("&")[0].strip()
        log.info(f"fetching data for country: {country_code}")
        offset = 0
        total_count = None
        count = 0
        while True:
            final_url = (
                search_url.split("&offset=")[0].strip()
                + "&offset="
                + str(offset)
                + "&"
                + search_url.split("&offset=")[1].strip().split("&", 1)[1].strip()
            )
            stores_req = session.get(final_url, headers=headers)

            if count == 0:
                total_count = json.loads(stores_req.text)["response"]["count"]
                count = count + 1

            if offset < total_count:
                stores = json.loads(stores_req.text)["response"]["entities"]
                for store in stores:
                    try:
                        page_url = store["websiteUrl"]["url"]
                        page_url = page_url.split("?utm_source")[0].strip()
                    except:
                        page_url = "<MISSING>"
                        pass

                    if page_url == "http://www.lepainquotidien.us":
                        page_url = "<MISSING>"
                    locator_domain = website
                    location_name = store["name"]

                    store_number = "<MISSING>"

                    street_address = store["address"]["line1"]
                    if "line2" in store:
                        street_address = street_address + ", " + store["line2"]

                    city = store["address"].get("city", "<MISSING>")
                    state = store["address"].get("region", "<MISSING>")
                    zip = store["address"].get("postalCode", "<MISSING>")

                    phone = ""
                    if "mainPhone" in store:
                        phone = store["mainPhone"]

                    location_type = "<MISSING>"
                    if "-" in location_name:
                        location_name = store["name"].split("-")[0].strip()
                        location_type = store["name"].split("-")[1].strip()

                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    if "geocodedCoordinate" in store:
                        latitude = store["geocodedCoordinate"]["latitude"]
                        longitude = store["geocodedCoordinate"]["longitude"]

                    hours_of_operation = ""
                    hours_list = []
                    if "hours" in store:
                        hours = store["hours"]
                        for hour in hours.keys():
                            if "openIntervals" in hours[hour]:
                                time = (
                                    hours[hour]["openIntervals"][0]["start"]
                                    + "-"
                                    + hours[hour]["openIntervals"][0]["end"]
                                )

                                hours_list.append(hour + ":" + time)

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

            else:
                break

            offset = offset + 50


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
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
