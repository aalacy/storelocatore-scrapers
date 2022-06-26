# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "thejuicycrab.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.thejuicycrab.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://www.thejuicycrab.com/locations",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.thejuicycrab.com/locations-data"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        stores = json.loads(
            "".join(search_sel.xpath('//textarea[@id="locations-data"]/text()')).strip()
        )["locations"]["objects"]

        for store in stores:

            if store["type"]["name"] != "Restaurant":
                continue

            page_url = "https://www.thejuicycrab.com/restaurant/" + store["hs_path"]

            locator_domain = website

            street_address = (
                store["address"].replace("<span>", "").replace("</span>", "").strip()
            )

            city = store["city"]
            state = store["state"]
            zip = "<MISSING>"

            country_code = "US"

            location_name = store["name"]

            phone = store["phone_number"]
            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_sel = lxml.html.fromstring(
                store["bussiness_hours"]
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .strip()
            )
            hours_of_operation = "; ".join(
                list(filter(str, [x.strip() for x in hours_sel.xpath("//p/text()")]))
            ).strip()
            if len(hours_of_operation) <= 0:
                hours = hours_sel.xpath("//table//tr")
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("td[1]/text()")).strip()
                    time = "".join(hour.xpath("td[2]/text()")).strip()
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = (
                store["lat"],
                store["long"],
            )
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
